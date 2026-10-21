"""Nota capturada a mano a partir del enlace al periódico.

El editor pega el enlace y la fecha; aquí se localiza el `Article` que el
scraper por lotes produce para ese día (o se raspa el listado si el día
no tiene lote), se liga a la nota, se genera el adjunto y se corren las
pasadas de Gemini que el artículo aún no tenga. El cotejo enlace →
artículo vive en `link_match`. Un enlace de un medio sin scraper no
bloquea el alta: la nota se guarda sin artículo (`LinkNotFetchable`).

La vista solo hace las validaciones baratas (`check_link`) y responde de
inmediato; el resto corre en un hilo (`launch_pipeline`, adr-0002) que
deja su desenlace en `Note.comments`. `fetch_note_from_link` es la misma
cadena sin hilo ni comentario, para el diagnóstico.
"""
import inspect
import threading
import time
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, List
from urllib.parse import urlsplit

from django.db import connections, transaction
from django.utils import timezone

from profile_auth.models import User
from source import link_match
from source.link_match import LinkMatchError, normalize_url
from source.models import Article, Note, NoteFile, ScrapedRecord, Source
from source.pdf_import.utils import (
    LEGACY_FROM_DATE, LEGACY_TO_DATE, get_synthetic_scraped_record)
from source.scraper.articles import CriteriaError, ManagerScraper

NOT_FOUND_MSG = "No pudimos extraer la nota del enlace"
DUPLICATE_MSG = "Esa nota ya existe en el sistema"
QUEUED_MSG = ("El contenido completo se buscará y descargará en unos "
              "minutos; regresa después.")
NOT_FETCHABLE_MSG = ("Este medio no se trae automáticamente; la nota se "
                     "guardó sin artículo")
COMMENT_AUTHOR = "Sistema"

# Proceso se lee de PressReader: las URLs de sus artículos no viven en el
# dominio de la revista, y un editor puede pegar cualquiera de las dos.
# La Jornada también publica bajo `web.`.
HOST_ALIASES = {
    "proceso.pressreader.com": "proceso.com.mx",
    "web.jornada.com.mx": "jornada.com.mx",
}
MONTHLY_HOSTS = {"proceso.com.mx"}

# Orden estricto: cada pasada lee la salida de la anterior.
GEMINI_STAGES = ("first", "second", "precapture")
STAGE_LABELS = {
    "first": "la primera pasada de Gemini",
    "second": "la segunda pasada de Gemini",
    "precapture": "la precaptura de Gemini",
}
REUSED_LABELS = {
    "first": "primera pasada",
    "second": "segunda pasada",
    "precapture": "precaptura",
}
MATCH_LABELS = {
    "gemini": "por Gemini",
    "containment": "por contención",
    "title_fuzzy": "por similitud",
}
FETCH_BUTTON = "Traer información del enlace"

# Los artículos que pdf_import fabrica para notas legadas no vienen de
# ningún listado: su presencia no dice que el día ya se haya raspado.
PDF_IMPORT_UID_PREFIX = "pdf-note-"


class NoteFromLinkError(Exception):
    """Fallo que impide ligar la nota a un artículo."""

    def __init__(self, reason: str, detail: str = NOT_FOUND_MSG,
                 **extra) -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail = detail
        self.extra = extra

    def as_response(self) -> dict:
        return {"detail": self.detail, "reason": self.reason, **self.extra}


class LinkNotFetchable(NoteFromLinkError):
    """El enlace no es de un medio con scraper: la nota va sin artículo."""


@dataclass
class PipelineReport:
    stages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timings: dict = field(default_factory=dict)
    match: dict = field(default_factory=dict)
    # Pasadas que el lote ya había corrido sobre el artículo.
    reused: List[str] = field(default_factory=list)
    # Desenlaces que no son error pero cambian el comentario:
    # `no_generator`, `had_files`, `empty_precapture`, `frozen`,
    # `precapture_exists`.
    flags: set = field(default_factory=set)
    # Pasada de Gemini que tumbó la cadena; con ella se deshace el enlace.
    failed_stage: str | None = None
    stage_error: str = ""

    def timed(self, stage: str, func: Callable, *args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            self.timings[stage] = round(
                self.timings.get(stage, 0) + time.monotonic() - start, 2)

    def summary(self, article: Article | None = None) -> dict:
        data = {
            "stages": self.stages,
            "reused": self.reused,
            "errors": self.errors,
            "flags": sorted(self.flags),
            "failed_stage": self.failed_stage,
            "match": self.match,
            "timings": self.timings,
        }
        if article is not None:
            data["article"] = article.id
            data["certainty_degree"] = article.certainty_degree
            data["second_certainty_degree"] = (
                article.second_certainty_degree)
        return data


@dataclass
class PreparedArticle:
    source: Source
    article: Article
    report: PipelineReport


def link_host(url: str | None) -> str:
    host = urlsplit((url or "").strip()).netloc.lower()
    host = host.split(":")[0].removeprefix("www.")
    return HOST_ALIASES.get(host, host)


def resolve_source(link: str) -> Source:
    host = link_host(link)
    if not host:
        raise LinkNotFetchable("El enlace no es una URL válida.")
    for source in Source.objects.exclude(main_url__isnull=True):
        if link_host(source.main_url) == host:
            return source
    raise LinkNotFetchable(f"Dominio sin fuente registrada: {host}")


def get_manager_class(source: Source) -> type[ManagerScraper]:
    # Import diferido: el despachador vive en la vista de scraping, que
    # importa los scrapers de todas las fuentes.
    from api.views.scraping.views import get_manager_scraper_class
    try:
        return get_manager_scraper_class(source)
    except Exception:
        raise LinkNotFetchable(
            f"La fuente «{source.name}» no tiene scraper.")


def is_link_fetchable(link: str | None) -> bool:
    """Sin red: el dominio tiene fuente y la fuente tiene scraper."""
    if not link:
        return False
    try:
        get_manager_class(resolve_source(link))
    except NoteFromLinkError:
        return False
    return True


def is_monthly(source: Source) -> bool:
    return link_host(source.main_url) in MONTHLY_HOSTS


def edition_date(source: Source, date_: date) -> date:
    # Proceso es mensual: su edición se resuelve por el día 1 del mes.
    if is_monthly(source):
        return date_.replace(day=1)
    return date_


def edition_bounds(source: Source, day: date) -> tuple[date, date]:
    if not is_monthly(source):
        return day, day
    last = monthrange(day.year, day.month)[1]
    return day.replace(day=1), day.replace(day=last)


def build_manager(
        source: Source, record: ScrapedRecord) -> ManagerScraper:
    manager_class = get_manager_class(source)
    return manager_class("", "", recover_record=record)


def edition_articles(source: Source, day: date) -> List[Article]:
    # Los artículos de Proceso no siempre caen en el día 1 (hubo números
    # fechados el 3 o el 4): la edición es el mes entero.
    first, last = edition_bounds(source, day)
    return list(Article.objects.filter(
        source=source, published_date__range=(first, last)))


def is_listed(article: Article) -> bool:
    return not (article.uid or "").startswith(PDF_IMPORT_UID_PREFIX)


def covering_record(source: Source, day: date) -> ScrapedRecord | None:
    # Solo lotes reales: el sintético de pdf_import cubre 2017-2023 sin
    # haber raspado nada. Los lotes de Proceso van del 1 al último del
    # mes; basta con que uno toque el mes.
    first, last = edition_bounds(source, day)
    return ScrapedRecord.objects.filter(
        source=source, from_date__lte=last, to_date__gte=first,
    ).exclude(
        from_date=LEGACY_FROM_DATE, to_date=LEGACY_TO_DATE,
    ).order_by("-from_date").first()


def scrape_day_listing(source: Source, day: date) -> List[Article]:
    """Raspa el listado de un día sin lote y registra sus artículos.

    Cuelgan del registro sintético de la fuente: un lote de un día
    bloquearía por traslape la corrida por lotes que después cubra la
    fecha, y esa corrida reclama los artículos del sintético al
    encontrarlos (`record_article`).
    """
    manager = build_manager(source, get_synthetic_scraped_record(source))

    # La fórmula del uid toma la fecha tal como la recibe el scraper del
    # día; con otro formato saldrían uids que el lote no deduplica.
    day_key = day.strftime(manager.date_format)
    main_class = manager.main_scraper_class
    kwargs = {}
    # El de Proceso no recibe sesión: va por PressReader, no por la web.
    if "session" in inspect.signature(main_class.__init__).parameters:
        kwargs["session"] = manager.session
    try:
        sections = main_class(day_key, **kwargs).sections_dict
    except Exception as exc:
        raise NoteFromLinkError(f"No se pudo leer el índice del día: {exc}")

    for section_name, section_data in sections.items():
        for article_data in section_data.get("articles", []):
            try:
                manager.record_article(article_data, section_name, day_key)
            except Exception as exc:
                article_data.setdefault("errors", []).append(str(exc))
    return edition_articles(source, day)


def scrape_article(article: Article) -> None:
    manager = build_manager(article.source, article.scraped)
    try:
        manager.full_scrape_article(article)
    except CriteriaError as exc:
        raise NoteFromLinkError(str(exc))
    article.refresh_from_db()


def ensure_title(article: Article, report: PipelineReport) -> bool:
    if article.title:
        return True
    # El listado de Reforma no trae títulos: solo los da el artículo
    # raspado, que el lote haría de todos modos.
    try:
        report.timed("scrape", scrape_article, article)
    except NoteFromLinkError as exc:
        report.errors.append(str(exc))
        return False
    return bool(article.title)


def match_article(
        candidates: List[Article], link: str, title: str,
        report: PipelineReport,
) -> Article | None:
    try:
        return link_match.match_article(
            candidates, link, title, report,
            lambda article: ensure_title(article, report))
    except LinkMatchError as exc:
        raise NoteFromLinkError(str(exc))


def check_duplicate(article: Article, note: Note | None) -> None:
    if article.note_id and (not note or article.note_id != note.id):
        raise NoteFromLinkError(
            f"El artículo ya está ligado a la nota {article.note_id}.",
            detail=DUPLICATE_MSG, note=article.note_id)


def check_link(
        link: str | None, date_: date, note: Note | None = None,
) -> Source:
    """Validaciones sin red ni IA, para responder 400 antes del hilo.

    El duplicado solo se detecta aquí si la URL ya está entre los
    artículos guardados del día; el cotejo por título lo vuelve a
    revisar dentro del hilo. `LinkNotFetchable` no es un rechazo: quien
    llama guarda la nota sin pipeline.
    """
    if not link:
        raise NoteFromLinkError("La nota no tiene enlace.")
    source = resolve_source(link)
    get_manager_class(source)
    day = edition_date(source, date_)
    wanted_url = normalize_url(link)
    by_url = [a for a in edition_articles(source, day)
              if normalize_url(a.url) == wanted_url]
    if len(by_url) == 1:
        check_duplicate(by_url[0], note)
    return source


def prepare_article(
        link: str, date_: date, title: str, note: Note | None = None,
) -> PreparedArticle:
    """Localiza (y raspa si hace falta) el artículo del enlace.

    Lanza `NoteFromLinkError` ante cualquier fallo; no toca la nota.
    Solo raspa el listado un día sin lote real ni artículos de un
    listado previo; si no, coteja contra lo guardado y, si el del
    enlace no está, falla.
    """
    report = PipelineReport()
    source = resolve_source(link)
    get_manager_class(source)
    day = edition_date(source, date_)

    candidates = edition_articles(source, day)
    has_batch = covering_record(source, day) is not None
    # Con lote, su listado es el del día: volver a rasparlo no traería
    # otra cosa. Los de pdf_import siguen como candidatos, pero no
    # cuentan como listado.
    if not has_batch and not any(is_listed(a) for a in candidates):
        candidates = report.timed(
            "listing", scrape_day_listing, source, day)
        report.stages.append("listing")
    if not candidates:
        batch_note = " (el día tiene lote de scraping)" if has_batch else ""
        raise NoteFromLinkError(
            f"No hay artículos de {source.name} para el {day}"
            f"{batch_note}.")

    try:
        article = report.timed(
            "match", match_article, candidates, link, title, report)
    except NoteFromLinkError as exc:
        exc.extra.setdefault("match", report.match)
        raise
    if not article:
        raise NoteFromLinkError(
            "Ningún artículo del día coincide con el enlace ni con el "
            "título.", match=report.match)
    report.stages.append("match")
    check_duplicate(article, note)

    if not article.paragraphs:
        report.timed("scrape", scrape_article, article)
        report.stages.append("scrape")
    if not article.paragraphs and not article.images:
        raise NoteFromLinkError("El artículo no trae texto.")
    if not article.published_date:
        article.published_date = day
        article.save(update_fields=["published_date"])
    return PreparedArticle(source=source, article=article, report=report)


def copy_article_fields(note: Note, article: Article) -> None:
    pages = article.pages
    if not pages:
        pagina = article.get_meta("pagina")
        pages = pagina.get("texto") if isinstance(pagina, dict) else None
    values = {
        "subtitle": article.subtitle, "author": article.author,
        "section": article.section, "pages": pages,
    }
    changed = [
        name for name, value in values.items()
        if value and not getattr(note, name)]
    for name in changed:
        setattr(note, name, values[name])
    if changed:
        note.save(update_fields=changed)


def is_empty_precapture(manager) -> bool:
    """La precaptura respondió una lista vacía: no hay menciones.

    `get_ai_criteria` no distingue `[]` de la falta de respuesta y lanza
    «No response AI service» en ambos casos; el lote lo deja así.
    """
    request = manager.classify_request
    parsed = getattr(request.response, "parsed", None)
    return request.last_error is None and parsed == []


def drop_last_error(article: Article) -> None:
    # CriteriaError ya anotó el falso fallo en el artículo.
    if article.errors:
        article.errors.pop()
        article.save(update_fields=["errors"])


def run_gemini_chain(
        note: Note, article: Article, report: PipelineReport,
        user: User | None = None,
) -> None:
    from source.criteria.first import FirstCriteriaManager
    from source.criteria.pre_capture import PreCaptureManager
    from source.criteria.second import SecondCriteriaManager

    # Una petición por artículo, sin caché de contexto. Solo corren las
    # pasadas que el artículo no tiene: la clasificación del lote nunca
    # se sobrescribe.
    managers = {
        "first": FirstCriteriaManager(recover_record=None),
        "second": SecondCriteriaManager(recover_record=None),
        "precapture": PreCaptureManager(user=user),
    }
    done_by_batch = {
        "first": article.criteria,
        "second": article.second_criteria,
        "precapture": article.pre_capture,
    }
    for stage in GEMINI_STAGES:
        if stage == "precapture" and note.frozen_pre_capture:
            report.flags.add("frozen")
            return
        manager = managers[stage]
        if done_by_batch[stage]:
            report.reused.append(stage)
            if stage == "precapture":
                reuse_precapture(note, article, manager, report)
            continue
        try:
            manager.build_gemini_request()
            report.timed(stage, manager.get_ai_criteria, article)
        except CriteriaError as exc:
            if stage == "precapture" and is_empty_precapture(manager):
                drop_last_error(article)
                report.flags.add("empty_precapture")
                report.stages.append(stage)
                return
            fail_stage(report, stage, exc)
            return
        except Exception as exc:
            fail_stage(report, stage, exc)
            return
        report.stages.append(stage)


def reuse_precapture(
        note: Note, article: Article, manager, report: PipelineReport,
) -> None:
    """Copia a la nota la precaptura que el lote ya dejó en el artículo.

    `save_criteria_results` sin JSON nuevo rehidrata `article.pre_capture`
    y solo lo copia a `pre_mentions` si la nota no tiene menciones.
    """
    if note.mentions.exists():
        report.flags.add("precapture_exists")
        return
    try:
        manager.save_criteria_results(None, None, article)
    except Exception as exc:
        fail_stage(report, "precapture", exc)


def fail_stage(report: PipelineReport, stage: str, exc: Exception) -> None:
    report.errors.append(f"{stage}: {exc}")
    report.failed_stage = stage
    report.stage_error = str(exc)


def unlink_article(article: Article, note_file: NoteFile | None) -> None:
    """Suelta el artículo de la nota para que el editor reintente.

    El artículo raspado y sus párrafos se quedan: el reintento los
    reutiliza. Solo se borra el adjunto que generó esta corrida.
    """
    article.note = None
    article.save(update_fields=["note"])
    if note_file is not None:
        # La señal post_delete retira también el archivo en storage.
        note_file.delete()


def fill_note_from_article(
        note: Note, prepared: PreparedArticle, user: User | None = None,
) -> PipelineReport:
    """Liga, adjunta y clasifica. Reporta los fallos; no los lanza.

    Si una pasada de Gemini falla, deshace el enlace y el adjunto de
    esta corrida (`unlink_article`).
    """
    from source.attachment import (
        generate_attachment, get_attachment_generator)

    article, report = prepared.article, prepared.report
    article.note = note
    article.save(update_fields=["note"])
    if user:
        note.editors.add(user)

    # El adjunto va antes de copiar campos: trae el código de la página
    # real, y `metadata["pagina"]` puede ser el de la portada de sección.
    note_file = None
    if note.files.exists():
        report.flags.add("had_files")
    elif not get_attachment_generator(note.source):
        report.flags.add("no_generator")
    else:
        note_file = report.timed(
            "attachment", generate_attachment, article, note=note)
        if note_file:
            report.stages.append("attachment")
        else:
            report.errors.append("attachment: no se pudo generar")
    # Recargar justo antes de la precaptura, que guarda la nota completa:
    # lo que el editor cambió mientras corría el hilo (estatus incluido)
    # no se pisa con la copia vieja.
    note.refresh_from_db()
    copy_article_fields(note, article)

    run_gemini_chain(note, article, report, user=user)
    if report.failed_stage:
        unlink_article(article, note_file)
    article.refresh_from_db()
    return report


def fetch_note_from_link(
        note: Note, user: User | None = None) -> PipelineReport:
    """Cadena completa sobre una nota guardada; lanza si no hay artículo."""
    if not note.link:
        raise NoteFromLinkError("La nota no tiene enlace.")
    prepared = prepare_article(note.link, note.date, note.title, note=note)
    if note.source_id != prepared.source.id:
        note.source = prepared.source
        note.save(update_fields=["source"])
    return fill_note_from_article(note, prepared, user=user)


def join_es(items: List[str]) -> str:
    if len(items) < 3:
        return " y ".join(items)
    return f"{', '.join(items[:-1])} y {items[-1]}"


def success_comment(report: PipelineReport) -> str:
    done = ["Artículo"]
    if "attachment" in report.stages:
        done.append("adjunto")
    ran = ("precapture" in report.stages
           and "empty_precapture" not in report.flags)
    reused = ("precapture" in report.reused
              and "precapture_exists" not in report.flags)
    if ran or reused:
        done.append("precaptura")
    ready = "listo" if len(done) == 1 else "listos"
    text = join_es(done)
    notes = []
    how = MATCH_LABELS.get(report.match.get("by"))
    if how:
        best = report.match.get("best_title", "")
        notes.append(f"emparejada {how} con «{best}»")
    if report.reused:
        listed = join_es([REUSED_LABELS[stage] for stage in report.reused])
        notes.append(f"se reutilizó la clasificación del lote: {listed}")
    if "precapture_exists" in report.flags:
        notes.append("precaptura ya existente; la nota ya tenía menciones "
                     "y no se copió")
    if "no_generator" in report.flags:
        notes.append("esta fuente no genera adjunto")
    if "had_files" in report.flags:
        notes.append("la nota ya tenía adjunto")
    if "empty_precapture" in report.flags:
        notes.append("precaptura sin menciones relevantes")
    if "frozen" in report.flags:
        notes.append("la precaptura está congelada y no se tocó")
    if report.errors:
        notes.append(f"falló {'; '.join(report.errors)}")
    comment = f"{text} {ready}"
    if notes:
        comment += f" ({'; '.join(notes)})"
    return f"{comment}."


def rollback_comment(report: PipelineReport) -> str:
    stage = STAGE_LABELS.get(report.failed_stage, report.failed_stage)
    detail = report.stage_error.rstrip(".")
    reason = f" ({detail})" if detail else ""
    return (f"Se encontró el artículo, pero falló {stage}{reason}. Se "
            f"deshizo el enlace con el artículo y su adjunto; puedes "
            f"volver a presionar «{FETCH_BUTTON}».")


def outcome_comment(report: PipelineReport) -> str:
    if report.failed_stage:
        return rollback_comment(report)
    return success_comment(report)


def failure_comment(reason: str, match: dict | None = None) -> str:
    comment = f"{NOT_FOUND_MSG}: {reason.rstrip('.')}."
    best = (match or {}).get("best_title")
    if best:
        comment += f" La candidata más parecida fue «{best}»."
    if gemini_reason := (match or {}).get("gemini_reason"):
        comment += f" Gemini: {gemini_reason}"
    return comment


def sign(comment: str) -> str:
    # La firma del front (fecha y autor) más la hora: `add_comment` no
    # agrega un texto que ya esté, y un reintento con el mismo desenlace
    # se perdería.
    now = timezone.localtime().strftime("%d/%m/%Y %H:%M")
    return f"{now} - {COMMENT_AUTHOR}: {comment}"


def run_note_pipeline(note: Note, user: User | None = None) -> str:
    """Corre la cadena y deja su desenlace en `comments`. Nunca lanza.

    Ningún paso escribe `status_register`: un fallo deja la nota como
    estaba y, si el artículo no quedó ligado (no se encontró, o una
    pasada de Gemini deshizo el enlace), el botón del front sigue
    visible para reintentar.
    """
    try:
        report = fetch_note_from_link(note, user)
        comment = outcome_comment(report)
    except NoteFromLinkError as exc:
        comment = failure_comment(exc.reason, exc.extra.get("match"))
    except Exception as exc:
        comment = failure_comment(f"error inesperado: {exc}")
    note.refresh_from_db()
    note.add_comment(sign(comment))
    return comment


_running: set = set()
_running_lock = threading.Lock()


def pipeline_thread(note_id: int, user_id: int | None) -> None:
    try:
        note = Note.objects.get(pk=note_id)
        user = User.objects.filter(pk=user_id).first() if user_id else None
        run_note_pipeline(note, user)
    except Exception as exc:
        print(f"note_from_link: hilo de la nota {note_id} cayó: {exc}")
    finally:
        with _running_lock:
            _running.discard(note_id)
        # Django abre una conexión por hilo y solo cierra las de las
        # peticiones; la de este hilo quedaría abierta hasta que el
        # recolector la alcance.
        connections.close_all()


def launch_pipeline(note: Note, user: User | None = None) -> bool:
    """Lanza la cadena en un hilo. False si ya corre para esa nota.

    El candado es por proceso: dos workers distintos sí podrían correr
    la misma nota a la vez.
    """
    with _running_lock:
        if note.id in _running:
            return False
        _running.add(note.id)
    user_id = user.id if user and user.is_authenticated else None
    thread = threading.Thread(
        target=pipeline_thread, args=(note.id, user_id))
    # Con una transacción abierta, el hilo no vería la nota recién creada.
    transaction.on_commit(thread.start)
    return True
