"""Resolución determinista de los topónimos que la migración legada dejó
atorados en `Location.comments`.

`space_time/migrate/ubicacio.py` escribió ahí, con el prefijo `YEEKO:`,
el nombre de estado, municipio o localidad que no encontró en el
catálogo del INEGI, y también el caso contrario: el nombre que encontró
repetido y llenó a ciegas con el primer homónimo. Este módulo parte esos
comentarios, busca candidatos en el catálogo y dictamina qué hacer con
cada fragmento. No toca la base más que para leer.

La lógica vive aquí y no en el comando porque el backfill de
geolocalización tiene que aplicar el mismo dictamen.
"""

import re
import unicodedata
from collections import namedtuple

from rapidfuzz import fuzz, process

from actor.migrate.common import text_normalizer
from space_time.geolocate import without_placeholders
from space_time.models import Locality, Municipality

# Encabezados tal como los escribió `migrate/ubicacio.py`. El de "mismo
# nombre" va pegado al valor: al origen le falta el espacio.
HEADERS = [
    ("state_not_found", r"Estado no encontrado: "),
    ("municipality_not_found", r"Municipio no encontrado: "),
    ("locality_not_found", r"Localidad no encontrada: "),
    ("municipality_ambiguous",
     r"Se encontraron (?P<mun_n>\d+) municipios con el mismo nombre"),
    ("locality_ambiguous",
     r"Se encontraron (?P<loc_n>\d+) localidades con el mismo nombre"),
    ("geojson_error", r"Error al parsear el geojson"),
]
# Partir por `; ` rompe: el valor legado puede traerlo adentro. El corte
# lo marca el encabezado siguiente, no el separador.
HEADER_RE = re.compile(
    r"(?:^|; )(?:" + "|".join(f"(?P<{k}>{p})" for k, p in HEADERS) + r")")

PREFIX = "YEEKO:"

TEMPLATE_MUNICIPALITY = "municipio"
TEMPLATE_LOCALITY = "localidad"
TEMPLATE_HOMONYM = "homonimo"

TEMPLATE_BY_KIND = {
    "municipality_not_found": TEMPLATE_MUNICIPALITY,
    "locality_not_found": TEMPLATE_LOCALITY,
    "municipality_ambiguous": TEMPLATE_HOMONYM,
    "locality_ambiguous": TEMPLATE_HOMONYM,
}

EXACT = "exacto"
FUZZY = "fuzzy"
CONTAINED = "contenido"
NO_MATCH = "sin_match"
NO_SCOPE = "sin_ambito"
HOMONYM = "homonimo"

FILL = "llenar"
TO_DETAILS = "a_details"
UNRESOLVED = "sin_resolver"
EMPTY = "vaciar"

# Escala de `rapidfuzz`: 0 a 100.
FUZZY_MIN = 87
PARTIAL_MIN = 87
# «Taxco» → «Taxco de Alarcón» obliga a bajar a cinco; por debajo de eso
# el fragmento casa con demasiados candidatos y deja de ser único.
MIN_CONTAINED_LEN = 5

# Palabras que delatan un tipo 3: no son topónimos del catálogo sino
# colonias, parajes o descripciones de camino, y su destino es
# `Location.details`, no una llave foránea.
TYPE3_PATTERNS = [
    ("colonia", r"\bcolonia\b"),
    ("col.", r"\bcol\."),
    ("fracc", r"\bfracc"),
    ("ejido", r"\bejido\b"),
    ("barrio", r"\bbarrio\b"),
    ("carretera", r"\bcarretera\b"),
    ("km", r"\bkms?\b|\bkm\d"),
    ("presa", r"\bpresa\b"),
    ("rio", r"\brio\b"),
    ("cerro", r"\bcerro\b"),
    ("rancho", r"\brancho\b"),
    ("parque", r"\bparque\b"),
    ("zona", r"\bzona\b"),
]

Fragment = namedtuple("Fragment", "kind template value count verbatim")
Candidate = namedtuple("Candidate", "id name std")
Match = namedtuple("Match", "level candidate score")


def strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn")


def type3_signal(value: str) -> str:
    """Palabras de tipo 3 halladas, separadas por `|` (vacío si ninguna).

    Corre sobre el texto crudo en minúsculas y sin acentos, no sobre el
    normalizado: `text_normalizer` borra espacios y puntos, y sin ellos
    no hay frontera de palabra que buscar.
    """
    low = strip_accents((value or "").lower())
    hits = [word for word, pattern in TYPE3_PATTERNS
            if re.search(pattern, low)]
    return "|".join(hits)


def parse_yeeko_fragments(comments: str | None) -> list[Fragment]:
    """Fragmentos del bloque `YEEKO:` de un comentario."""
    if not comments or not comments.startswith(PREFIX):
        return []
    # Lo que un editor agregó a mano va después de un salto de línea.
    block = comments[len(PREFIX):].split("\n")[0].strip()
    matches = list(HEADER_RE.finditer(block))
    fragments = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        # `lastgroup` no sirve: los encabezados de homónimo llevan un
        # grupo anidado para la N y el anidamiento decide cuál gana.
        kind = next(k for k, _ in HEADERS if match.group(k) is not None)
        count = None
        if kind == "municipality_ambiguous":
            count = int(match.group("mun_n"))
        elif kind == "locality_ambiguous":
            count = int(match.group("loc_n"))
        fragments.append(Fragment(
            kind=kind,
            template=TEMPLATE_BY_KIND.get(kind),
            value=block[match.end():end].strip(),
            count=count,
            verbatim=block[match.start():end].lstrip("; ").strip()))
    return fragments


def _best(std: str, candidates: list[Candidate], scorer):
    """Mejor candidato bajo un scorer de `rapidfuzz`."""
    found = process.extractOne(
        std, [c.std for c in candidates], scorer=scorer)
    if not found:
        return None, 0.0
    _, score, position = found
    return candidates[position], score


def match_legacy_name(value: str, candidates: list[Candidate] | None) -> Match:
    """Dictamina el nivel de coincidencia de un valor legado.

    `candidates` en `None` significa que la ubicación no trae el ámbito
    exigido (municipio capturado para una localidad, estado para un
    municipio): sin ámbito no se busca, porque los homónimos a escala
    estatal o nacional son demasiados para decidir sin revisión.

    `partial_ratio` es lo que rescata «Cuajimalpa» → «Cuajimalpa de
    Morelos», donde el `ratio` completo se hunde por la diferencia de
    largo; a cambio dispara con cualquier subcadena, así que solo cuenta
    si un único candidato del ámbito la alcanza.

    Cuando nada alcanza el umbral se devuelve igual el mejor candidato,
    como material de revisión; el nivel `sin_match` es lo que manda.
    """
    if candidates is None:
        return Match(NO_SCOPE, None, 0.0)
    std = text_normalizer(value) or ""
    if not std or not candidates:
        return Match(NO_MATCH, None, 0.0)

    for candidate in candidates:
        if candidate.std == std:
            return Match(EXACT, candidate, 100.0)

    best, best_score = _best(std, candidates, fuzz.ratio)
    if best_score >= FUZZY_MIN:
        return Match(FUZZY, best, best_score)

    if len(std) >= MIN_CONTAINED_LEN:
        partial = process.extract(
            std, [c.std for c in candidates], scorer=fuzz.partial_ratio,
            score_cutoff=PARTIAL_MIN, limit=None)
        if len(partial) == 1:
            _, score, position = partial[0]
            return Match(CONTAINED, candidates[position], score)

    return Match(NO_MATCH, best, best_score)


def exact_homonyms(value: str, candidates: list[Candidate] | None):
    """Candidatos idénticos al valor: los homónimos que el legado llenó
    a ciegas con el primero."""
    if not candidates:
        return []
    std = text_normalizer(value) or ""
    if not std:
        return []
    return [c for c in candidates if c.std == std]


def verdict_for(level: str, signal: str, template: str) -> str:
    """Qué hacer con el fragmento.

    La señal de tipo 3 pesa más que cualquier coincidencia aproximada
    —son colonias y descripciones, no topónimos—, pero no más que una
    coincidencia exacta contra el catálogo, y no aplica a los
    municipios: su catálogo es cerrado y ahí «Barrio», «Río» o «Ejido»
    son parte del nombre oficial, no la seña de una colonia.

    El homónimo se vacía: el legado llenó la localidad a ciegas con el
    primero de varios con el mismo nombre, así que el valor guardado no
    tiene respaldo.
    """
    if level == HOMONYM:
        return EMPTY
    if level == EXACT:
        return FILL
    if signal and template != TEMPLATE_MUNICIPALITY:
        return TO_DETAILS
    if level in (FUZZY, CONTAINED):
        return FILL
    return UNRESOLVED


class CandidateIndex:
    """Catálogo normalizado y cacheado por ámbito.

    Normaliza sobre `name` y no sobre el `std_name` guardado porque
    `Locality` no tiene esa columna y así ambas capas se comparan con la
    misma regla.

    Las localidades se filtran igual que en el motor de geolocalización
    —vigentes y sin los marcadores «Ninguno» del AGEEML— para que un
    dictamen no llene lo que el motor nunca asignaría. `Municipality` no
    tiene equivalente: su catálogo es cerrado y no marca vigencia.
    """

    def __init__(self):
        self._cache = {}

    def localities(self, municipality_id) -> list[Candidate] | None:
        if not municipality_id:
            return None
        key = ("loc", municipality_id)
        if key not in self._cache:
            self._cache[key] = self._build(without_placeholders(
                Locality.objects.filter(
                    municipality_id=municipality_id, is_current=True)))
        return self._cache[key]

    def municipalities(self, state_id) -> list[Candidate] | None:
        if not state_id:
            return None
        key = ("mun", state_id)
        if key not in self._cache:
            self._cache[key] = self._build(
                Municipality.objects.filter(state_id=state_id))
        return self._cache[key]

    @staticmethod
    def _build(queryset) -> list[Candidate]:
        return [
            Candidate(pk, name, text_normalizer(name) or "")
            for pk, name in queryset.values_list("id", "name")]
