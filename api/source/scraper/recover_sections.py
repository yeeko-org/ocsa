"""Recupera hacia atrás las secciones de artículo único de La Jornada.

«Editorial» y «El Correo Ilustrado» nunca entraron por scraping: sus
URLs no son índices de sección sino el artículo mismo, y el scraper
buscaba contenedores de listado ([[adr-0004]] lo arregló hacia adelante).
Quedaron 456 días con la sección listada y cero artículos.

La unidad de trabajo es el `ScrapedRecord`: cada lote se completa entero
—scrape, primera pasada, segunda, pre-captura— antes de pasar al
siguiente. Eso hace viable el caché de contexto de Gemini, cuyo TTL es
una caducidad absoluta desde su creación y no sobreviviría a los 912
artículos de una sola pasada, y acota una interrupción a un solo lote.
"""
from typing import List, Tuple

from source.criteria.batch import classify_batch
from source.criteria.first import FirstCriteriaManager
from source.criteria.pre_capture import PreCaptureManager
from source.criteria.second import SecondCriteriaManager
from source.models import Article, ScrapedRecord, Source
from source.scraper.articles import CriteriaError
from source.scraper.jornada import (
    JORNADA_MAIN_URL, SINGLE_ARTICLE_SECTIONS, JornadaManagerScraper,
    absolutize_article, single_article_payload)
from source.scraper.scraper_base import ScraperSession
from profile_auth.models import User

Gap = Tuple[str, str, dict]


class SingleSectionRecovery:

    def __init__(
            self, limit_records: int | None = None, phase: str = "all",
            user: User | None = None, ai_engine: str | None = None
    ) -> None:
        self.limit_records = limit_records
        self.phase = phase
        self.user = user
        self.ai_engine = ai_engine
        self.created = 0
        self.reattached = 0
        self.scrape_failed: List[str] = []
        self.notes_created = 0
        self.aborted = False
        self.orphan_records: set = set()

    # ------------------------------------------------------------------
    # Enumeración
    # ------------------------------------------------------------------
    def get_records(self) -> List[ScrapedRecord]:
        source = Source.objects.get(main_url=JORNADA_MAIN_URL)
        records = ScrapedRecord.objects.filter(
            source=source).order_by("from_date")
        if self.phase == "classify":
            pending = [r for r in records if self.pending_ids(r)]
        else:
            # Sin `data` no hay nada que recorrer: cae aquí el lote
            # legacy de PDF, los marcadores y los lotes que fallaron.
            pending = [r for r in records if r.data and self.get_gaps(r)]
        if self.limit_records:
            pending = pending[:self.limit_records]
        return pending

    def pending_ids(self, record: ScrapedRecord) -> List[int]:
        """Artículos ya recuperados de esas secciones, aún sin clasificar."""
        return list(Article.objects.filter(
            scraped=record, section__in=SINGLE_ARTICLE_SECTIONS,
            criteria__isnull=True
        ).exclude(content__isnull=True).values_list("id", flat=True))

    def get_gaps(self, record: ScrapedRecord) -> List[Gap]:
        gaps: List[Gap] = []
        for day, sections in (record.data or {}).items():
            # Los días festivos guardan {"error", "exception"} en vez del
            # diccionario de secciones: no hubo edición, no es un fallo.
            if not isinstance(sections, dict):
                continue
            for name, payload in sections.items():
                if name not in SINGLE_ARTICLE_SECTIONS:
                    continue
                if not isinstance(payload, dict) or payload.get("error"):
                    continue
                if payload.get("articles") or not payload.get("url"):
                    continue
                gaps.append((day, name, payload))
        return gaps

    # ------------------------------------------------------------------
    # Ejecución
    # ------------------------------------------------------------------
    def run(self) -> None:
        records = self.get_records()
        if not records:
            print("No hay secciones de artículo único pendientes.")
            return

        if self.phase == "classify":
            total = sum(len(self.pending_ids(r)) for r in records)
            print(f"{total} artículos por clasificar en {len(records)} lotes")
            session = None
        else:
            total = sum(len(self.get_gaps(r)) for r in records)
            print(f"{total} día-sección por recuperar en "
                  f"{len(records)} lotes")
            # Una sola sesión para toda la corrida: el challenge de
            # Cloudflare se paga una vez, no una por lote.
            session = ScraperSession(
                with_proxy=True, warmup_url=JORNADA_MAIN_URL)

        for record in records:
            print(f"\nLote {record.id} "
                  f"({record.from_date} → {record.to_date})")
            if self.phase == "classify":
                article_ids = self.pending_ids(record)
            else:
                article_ids = self.recover_record(record, session)
            if self.phase == "scrape" or not article_ids:
                continue
            self.classify(article_ids)
            if self.aborted:
                print("Corrida detenida: fallos repetidos en la "
                      "clasificación (casi siempre, cuota agotada).")
                break

        self.drop_orphan_records()
        self.print_summary()

    def recover_record(
            self, record: ScrapedRecord, session: ScraperSession
    ) -> List[int]:
        manager = JornadaManagerScraper(
            "", "", recover_record=record, session=session)
        source = manager.get_source()
        article_ids: List[int] = []
        touched = False

        for day, name, payload in self.get_gaps(record):
            article_data = absolutize_article(
                single_article_payload(name, payload["url"]),
                day, f"{JORNADA_MAIN_URL}{day}/")
            existed = Article.objects.filter(
                uid=article_data["uid"], source=source).exists()
            manager.record_article(article_data, name, day)

            article = Article.objects.filter(
                uid=article_data["uid"], source=source).first()
            if not article:
                self.scrape_failed.append(article_data["uid"])
                continue
            if not existed:
                self.created += 1

            self.adopt_article(article, record)
            try:
                manager.full_scrape_article(article)
            except CriteriaError as e:
                self.scrape_failed.append(f"{article_data['uid']}: {e}")

            article.refresh_from_db()
            if not article.content:
                continue
            payload["articles"] = [article_data]
            article_ids.append(article.id)
            touched = True

        if touched:
            # Un solo save por lote: `data` de un lote mensual pesa
            # varios MB y guardarlo por día no compra nada.
            record.save()
        return article_ids

    def adopt_article(
            self, article: Article, record: ScrapedRecord) -> None:
        """Reclama un artículo que quedó colgado de un lote ajeno.

        El piloto que motivó [[adr-0005]] dejó diez editoriales en un
        `ScrapedRecord` marcador con fechas de 1900. Comparten `uid` con
        los que produce esta recuperación, así que `get_or_create` los
        devuelve tal cual y sin esto seguirían fuera de su lote.
        """
        if article.scraped_id == record.id:
            return

        orphan = article.scraped
        article.scraped = record
        # Su clasificación viene de una versión de prompt que no consta;
        # se rehace con la vigente junto al resto del lote.
        article.criteria = None
        article.certainty_degree = None
        article.save()
        self.reattached += 1
        if orphan and not orphan.data:
            self.orphan_records.add(orphan.id)

    # ------------------------------------------------------------------
    # Clasificación
    # ------------------------------------------------------------------
    def classify(self, article_ids: List[int]) -> None:
        first = list(Article.objects.filter(
            id__in=article_ids, criteria__isnull=True))
        result = classify_batch(
            first, FirstCriteriaManager, seconds_cache=10,
            ai_engine=self.ai_engine)
        if result.aborted:
            self.aborted = True
            return

        second = list(Article.objects.filter(
            id__in=article_ids, certainty_degree__gt=100,
            second_criteria__isnull=True))
        result = classify_batch(
            second, SecondCriteriaManager, seconds_cache=15,
            ai_engine=self.ai_engine)
        if result.aborted:
            self.aborted = True
            return

        pending = list(Article.objects.filter(
            id__in=article_ids, second_certainty_degree__gt=100,
            note__isnull=True))
        result = classify_batch(
            pending, PreCaptureManager, seconds_cache=30,
            ai_engine=self.ai_engine, user=self.user)
        self.notes_created += Article.objects.filter(
            id__in=[a.id for a in pending], note__isnull=False).count()
        if result.aborted:
            self.aborted = True

    def drop_orphan_records(self) -> None:
        for record_id in self.orphan_records:
            record = ScrapedRecord.objects.filter(pk=record_id).first()
            if record and not record.articles.exists():
                print(f"Lote {record_id} quedó vacío; se elimina.")
                record.delete()

    def print_summary(self) -> None:
        print(f"\nArtículos nuevos: {self.created} | "
              f"reasignados: {self.reattached} | "
              f"notas creadas: {self.notes_created} | "
              f"fallos de scrape: {len(self.scrape_failed)}")
        for failure in self.scrape_failed:
            print(f"  - {failure}")
