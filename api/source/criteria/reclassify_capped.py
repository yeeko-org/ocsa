"""Reclasifica los artículos que el veto de banderas dejó bajo el umbral.

`get_certainty_degree_v2` capa a 98 los marcados como opinión política y
a 97 los marcados como extranjeros, siempre que hubieran superado 100.
Como el umbral de paso es 100, el cap es un veto. [[adr-0006]] reescribió
el criterio de opinión política y [[adr-0007]] cambió el motor, así que
esos artículos merecen otra pasada con el criterio vigente.

El universo son los capados **por opinión política**, que es el único
criterio que [[adr-0006]] midió. Se excluyen los vetados por `is_foreign`
—tanto los que están en 97 como los que una versión anterior del cálculo
dejó en 98— porque reclasificarlos los liberaba sin que ninguna medición
lo respaldara: en la corrida local del 2026-08-02 los cuatro que subieron
por esa vía eran temas extranjeros o globales, justo lo que la bandera
debía vetar.
"""
from collections import Counter
from typing import List

from source.criteria.batch import classify_batch
from source.criteria.first import FirstCriteriaManager
from source.criteria.second import SecondCriteriaManager
from source.models import Article

# Los dos valores que produce el cap. No son el universo de entrada —eso
# lo fija `get_articles`— sino cómo se reconoce que un artículo salió
# vetado otra vez: puede volver a caer en 98, o en 97 si ahora lo marca
# como extranjero.
CAPPED_DEGREES = [97, 98]


def _snapshot(articles: List[Article]) -> dict:
    """Valores previos, solo escalares.

    `save_criteria_results` reemplaza el dict de `criteria` del mismo
    objeto en memoria, así que guardar una referencia no serviría.
    """
    snap = {}
    for article in articles:
        criteria = article.criteria or {}
        snap[article.id] = {
            "degree": article.certainty_degree,
            "opinion": bool(criteria.get("is_political_opinion")),
            "foreign": bool(criteria.get("is_foreign")),
            "projects": len(criteria.get("projects") or []),
        }
    return snap


class CappedReclassifier:

    def __init__(
            self, chunk_size: int = 60, limit: int | None = None,
            only_first: bool = False, ai_engine: str | None = None
    ) -> None:
        self.chunk_size = chunk_size
        self.limit = limit
        self.only_first = only_first
        self.ai_engine = ai_engine
        self.recovered: List[Article] = []
        self.still_capped = 0
        self.dropped: List[int] = []
        self.flag_cleared_low = 0
        self.skipped_no_content: List[int] = []
        self.aborted = False
        self.touched_ids: List[int] = []

    def get_articles(self) -> List[Article]:
        articles = Article.objects.filter(
            certainty_degree=98, criteria__is_political_opinion=True
        ).select_related("source").order_by("id")
        if self.limit:
            articles = articles[:self.limit]
        return list(articles)

    def run(self) -> None:
        articles = self.get_articles()
        if not articles:
            print("No hay artículos capados a 97/98.")
            return

        print(f"Reclasificando {len(articles)} artículos capados "
              f"(chunks de {self.chunk_size})")

        for start in range(0, len(articles), self.chunk_size):
            chunk = articles[start:start + self.chunk_size]
            if not self._run_chunk(chunk):
                self.aborted = True
                print("Corrida detenida: el lote abortó por fallos "
                      "repetidos (casi siempre, cuota agotada).")
                break

        if not self.only_first and not self.aborted:
            self._run_second_pass()

        self._print_summary()

    def _run_chunk(self, chunk: List[Article]) -> bool:
        before = _snapshot(chunk)
        result = classify_batch(
            chunk, FirstCriteriaManager, seconds_cache=10,
            ai_engine=self.ai_engine)
        self.skipped_no_content.extend(result.skipped_no_content)

        ids = [a.id for a in chunk if a.id not in result.skipped_no_content]
        self.touched_ids.extend(ids)
        for article in Article.objects.filter(
                id__in=ids).select_related("source"):
            self._classify_move(article, before[article.id])

        return not result.aborted

    def _classify_move(self, article: Article, before: dict) -> None:
        degree = article.certainty_degree or 0
        criteria = article.criteria or {}
        opinion = bool(criteria.get("is_political_opinion"))
        foreign = bool(criteria.get("is_foreign"))

        if degree > 100:
            self.recovered.append(article)
            return

        if degree in CAPPED_DEGREES:
            self.still_capped += 1
        elif before["projects"] and not (criteria.get("projects") or []):
            # Perdió los proyectos que antes sí detectaba: es el §1
            # moviéndose, no el criterio de opinión.
            self.dropped.append(article.id)

        cleared = (before["opinion"] and not opinion) or (
            before["foreign"] and not foreign)
        if cleared:
            self.flag_cleared_low += 1

    def _run_second_pass(self) -> None:
        pending = list(Article.objects.filter(
            id__in=self.touched_ids, certainty_degree__gt=100,
            second_criteria__isnull=True))
        if not pending:
            print("Segunda pasada: nada que clasificar")
            return

        print(f"Segunda pasada sobre {len(pending)} artículos")
        for start in range(0, len(pending), 40):
            chunk = pending[start:start + 40]
            result = classify_batch(
                chunk, SecondCriteriaManager, seconds_cache=15,
                ai_engine=self.ai_engine)
            if result.aborted:
                print("Segunda pasada detenida por fallos repetidos.")
                break

    def _print_summary(self) -> None:
        print("\n--- Movimiento ---")
        print(f"  recuperados (>100):        {len(self.recovered):5}")
        print(f"  siguen capados (97/98):    {self.still_capped:5}")
        print(f"  bajan (pierden proyectos): {len(self.dropped):5}")
        print(f"  pierden la bandera pero siguen <=100: "
              f"{self.flag_cleared_low}")
        if self.skipped_no_content:
            print(f"  sin contenido, no enviados: "
                  f"{len(self.skipped_no_content)}")

        if self.recovered:
            print("\n--- Recuperados por fuente ---")
            for name, count in Counter(
                    a.source.name for a in self.recovered).most_common():
                print(f"  {count:4}  {name}")
            print("\n--- Recuperados por sección ---")
            for section, count in Counter(
                    a.section or "(sin sección)"
                    for a in self.recovered).most_common(15):
                print(f"  {count:4}  {section}")
            print("\n--- Casos recuperados ---")
            for article in self.recovered:
                print(f"  [{article.id}] {article.certainty_degree} · "
                      f"{article.section} · {article.title}")

        if self.dropped:
            print(f"\n--- Bajan: {self.dropped}")
