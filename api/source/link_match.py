"""Cotejo del enlace de una nota contra los artículos de su día.

URL normalizada → título exacto → contención → difuso → Gemini, en ese
orden. No sabe raspar: quien llama le pasa cómo asegurar que un
candidato tenga título (`ensure_title`) y un reporte donde anotar cómo
se resolvió (`report.match`) y cuánto tardó Gemini (`report.timed`).
"""
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Callable, List
from urllib.parse import urlsplit

from source.base_models import LinkMatchResult
from source.criteria import make_gemini_request
from source.models import Article

TITLE_MATCH_THRESHOLD = 0.85
CONTAINMENT_MIN_WORDS = 3
# No cuentan para el mínimo: «De la tierra» no es un título distintivo.
STOPWORDS = frozenset((
    "de", "del", "la", "el", "los", "las", "en", "a", "y", "al", "con",
    "por", "para", "un", "una", "que", "se", "su"))
GEMINI_MAX_CANDIDATES = 20


class LinkMatchError(Exception):
    """Gemini no respondió: no hay veredicto, ni positivo ni negativo."""


def normalize_title(text: str | None) -> str:
    # NFKD separa los acentos y Cf atrapa los guiones suaves (U+00AD) que
    # PressReader siembra dentro de las palabras de Proceso.
    decomposed = unicodedata.normalize("NFKD", text or "")
    kept = "".join(
        char for char in decomposed
        if unicodedata.category(char) not in ("Mn", "Cf"))
    kept = re.sub(r"[^\w\s]|_", " ", kept.lower())
    return re.sub(r"\s+", " ", kept).strip()


def normalize_url(url: str | None) -> str:
    parts = urlsplit((url or "").strip())
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/")
    query = f"?{parts.query.lower()}" if parts.query else ""
    return f"{host}{path.lower()}{query}"


class LinkMatcher:
    """Último recurso del cotejo: Gemini elige entre los títulos impresos.

    El título web y el impreso de una misma nota pueden no compartir ni
    la mitad de las palabras; ningún umbral de `difflib` los separa de
    las notas vecinas sin aceptar también falsos positivos.
    """

    prompt_name = "link_match"
    version = "v1"
    seconds_cache = 2

    def __init__(self, ai_engine: str | None = None) -> None:
        self.ai_engine = ai_engine

    def build_content(
            self, link: str, title: str, candidates: List[Article]) -> str:
        lines = [f"Enlace: {link}", f"Título web: {title}", "",
                 "Candidatas:"]
        for number, article in enumerate(candidates, start=1):
            section = f" (sección: {article.section})" \
                if article.section else ""
            lines.append(f"{number}. {article.title.strip()}{section}")
        return "\n".join(lines)

    def choose(
            self, link: str, title: str, candidates: List[Article],
    ) -> tuple[Article | None, str]:
        request = make_gemini_request(self, prompt_segment="")
        content = self.build_content(link, title, candidates)
        result = request.send_gemini_prompt(
            content, schema_clss=LinkMatchResult, main_name="consulta")
        if result is None:
            raise LinkMatchError(
                f"Gemini no respondió al cotejar títulos: "
                f"{request.last_error}")
        answer = LinkMatchResult.model_validate(result)
        number = answer.candidate
        if not answer.matched or not number \
                or not 1 <= number <= len(candidates):
            return None, answer.reason
        return candidates[number - 1], answer.reason


def content_words(words: List[str]) -> int:
    return sum(1 for word in words if word not in STOPWORDS)


def match_by_title(
        candidates: List[Article], title: str, link: str, report,
        ensure_title: Callable[[Article], bool],
) -> Article | None:
    """Exacto → contención → difuso → Gemini, en ese orden."""
    wanted = normalize_title(title)
    wanted_words = set(wanted.split())
    titled = []
    for article in candidates:
        # Se asegura uno a uno: un título exacto corta el recorrido antes
        # de raspar los candidatos que faltan.
        if not ensure_title(article):
            continue
        candidate = normalize_title(article.title)
        if not candidate:
            continue
        if candidate == wanted:
            report.match = {"by": "title", "ratio": 1.0}
            return article
        ratio = SequenceMatcher(None, wanted, candidate).ratio()
        titled.append((article, candidate.split(), ratio))
    if not titled:
        return None

    contained = [
        item for item in titled
        if content_words(item[1]) >= CONTAINMENT_MIN_WORDS
        and set(item[1]) <= wanted_words]
    if contained:
        article, words, ratio = max(
            contained, key=lambda item: (len(item[1]), item[2]))
        report.match = {"by": "containment", "ratio": round(ratio, 3),
                        "best_title": article.title}
        return article

    titled.sort(key=lambda item: item[2], reverse=True)
    best, _, best_ratio = titled[0]
    report.match = {"by": "title_fuzzy", "ratio": round(best_ratio, 3),
                    "best_title": best.title}
    if best_ratio >= TITLE_MATCH_THRESHOLD:
        return best

    shortlist = [item[0] for item in titled[:GEMINI_MAX_CANDIDATES]]
    chosen, reason = report.timed(
        "gemini_match", LinkMatcher().choose, link, title, shortlist)
    report.match.update({"by": "gemini", "gemini_reason": reason})
    if chosen:
        report.match["best_title"] = chosen.title
    return chosen


def match_article(
        candidates: List[Article], link: str, title: str, report,
        ensure_title: Callable[[Article], bool],
) -> Article | None:
    wanted_url = normalize_url(link)
    by_url = [a for a in candidates if normalize_url(a.url) == wanted_url]
    if len(by_url) == 1:
        report.match = {"by": "url"}
        return by_url[0]
    # Varias piezas pueden compartir URL (la página de PressReader): el
    # título desempata entre ellas.
    pool = by_url or candidates
    return match_by_title(pool, title, link, report, ensure_title)
