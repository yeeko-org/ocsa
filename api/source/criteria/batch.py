"""Clasificación de listas de artículos que no forman un lote.

Los managers de `source/criteria/` seleccionan por `ScrapedRecord`, que
es lo correcto para el flujo normal. Las recuperaciones históricas y las
reclasificaciones trabajan sobre conjuntos que cruzan decenas de lotes,
así que arman la lista aparte y la pasan a `build_criteria(articles=...)`.

Este módulo envuelve esa llamada con lo que hace falta para que un
conjunto sin lote no rompa nada.
"""
from dataclasses import dataclass, field
from typing import List, Type

from source.criteria import BaseCriteriaManager
from source.models import Article
from profile_auth.models import User


@dataclass
class BatchResult:
    total: int = 0
    # Enviados a Gemini, no necesariamente clasificados: el fallo por
    # artículo se anota en `Article.errors`, no aquí.
    attempted: int = 0
    skipped_no_content: List[int] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    aborted: bool = False


def has_content(article: Article) -> bool:
    """Si no hay nada que mandar, clasificarlo solo produce un error.

    Importa más de lo que parece: el error de artículo vacío no lleva
    `status`, y el cortacircuitos de [[adr-0010]] compara el status con
    el anterior para contar la racha. Cinco artículos vacíos seguidos
    darían `None == None` cinco veces y abortarían el lote entero.
    """
    return bool(article.paragraphs or article.images)


class DetachedBatchMixin:
    """Manager que corre sin `ScrapedRecord` al cual reportar.

    Los errores se acumulan en memoria en vez de escribirse en el
    `errors` de un lote histórico que el editor ya dio por cerrado, y el
    cierre de lote se anula porque no hay lote que cerrar.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.batch_errors: List[str] = []

    def add_errors(self, errors: List[str]) -> None:
        self.batch_errors.extend(errors)
        for error in errors:
            print(error)

    def post_process_batch(self) -> None:
        return None


_detached_cache: dict = {}


def detached(manager_class: Type[BaseCriteriaManager]) -> Type:
    if manager_class not in _detached_cache:
        _detached_cache[manager_class] = type(
            f"Detached{manager_class.__name__}",
            (DetachedBatchMixin, manager_class), {})
    return _detached_cache[manager_class]


def classify_batch(
        articles: List[Article],
        manager_class: Type[BaseCriteriaManager],
        seconds_cache: int | None = None,
        ai_engine: str | None = None,
        user: User | None = None,
) -> BatchResult:
    """Corre una pasada de criterios sobre `articles` y resume qué pasó."""
    result = BatchResult(total=len(articles))
    if not articles:
        return result

    usable = []
    for article in articles:
        if has_content(article):
            usable.append(article)
        else:
            result.skipped_no_content.append(article.id)

    if not usable:
        return result

    kwargs = {"recover_record": None, "ai_engine": ai_engine}
    if user is not None:
        kwargs["user"] = user
    manager = detached(manager_class)(**kwargs)
    if seconds_cache:
        # Atributo de clase, pero el TTL que sirve depende del tamaño
        # real del chunk, no del flujo.
        manager.seconds_cache = seconds_cache

    manager.build_criteria(articles=usable)

    result.errors = manager.batch_errors
    result.aborted = any(
        "Lote abortado" in error for error in manager.batch_errors)
    result.attempted = len(usable)
    return result
