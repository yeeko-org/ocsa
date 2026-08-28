"""Dictámenes por ubicación que el backfill aplica antes que el motor.

`space_time/legacy_names.py` parte los comentarios `YEEKO:` que dejó la
migración legada y propone un veredicto por fragmento; un humano los
revisó y el resultado vive en los CSV de `.claude/`. Este módulo los
carga y los aplica sobre el objeto en memoria: llena la llave foránea
que el legado no supo resolver, manda a `details` lo que no es un
topónimo del catálogo, vacía lo que se llenó a ciegas con un homónimo,
y en todos esos casos borra del comentario el fragmento ya atendido.

No escribe en la base ni guarda: eso es del comando, que respalda
`comments` y `details` junto con lo demás para que `--revert` deshaga la
pasada entera.

El motor corre después, de modo que un municipio recién dictaminado ya
está puesto cuando la geometría resuelve la localidad.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from actor.migrate.common import text_normalizer
from space_time.legacy_names import (
    PREFIX, TEMPLATE_LOCALITY, TEMPLATE_MUNICIPALITY, parse_yeeko_fragments)

FILL = "llenar"
TO_DETAILS = "a_details"
EMPTY = "vaciar"
USELESS = "inutil"
# Veredictos que dejan el fragmento intacto: nadie pudo resolverlo, y el
# comentario sigue siendo el único registro de que ahí falta algo.
KEEP = frozenset({"sin_resolver", "irresoluble", "homonimo"})

DETAILS_LABEL = "Referencia legacy: "

# Capa que toca cada fragmento, por el encabezado que lo generó. Un
# homónimo vacía la capa que quedó ambigua, no siempre la localidad.
LAYER_BY_KIND = {
    "state_not_found": "state",
    "municipality_not_found": "municipality",
    "locality_not_found": "locality",
    "municipality_ambiguous": "municipality",
    "locality_ambiguous": "locality",
}
LAYER_BY_TEMPLATE = {
    TEMPLATE_MUNICIPALITY: "municipality",
    TEMPLATE_LOCALITY: "locality",
}
STATE_LAYERS = ("state", "municipality", "locality")


@dataclass
class FragmentVerdict:
    """Dictamen sobre un fragmento concreto de un comentario."""

    value: str
    verdict: str
    candidate_id: int | None
    source: str


@dataclass
class LayerVerdict:
    """Dictamen sobre la ubicación entera, por capa administrativa.

    Es la forma del CSV de estados: ahí el revisor no dictaminó
    fragmento por fragmento sino la tripleta que corresponde a toda la
    ubicación, y el comentario pierde los fragmentos de las capas que
    quedaron resueltas.
    """

    ids: dict
    source: str


@dataclass
class LocationVerdicts:
    fragments: dict = field(default_factory=dict)
    layers: LayerVerdict | None = None


def normalize(value: str | None) -> str:
    return text_normalizer(value or "") or ""


def _as_id(raw: str | None) -> int | None:
    """`candidate_id` numérico, o `None`.

    Los homónimos traen varios ids unidos por `|`: no identifican a
    nadie y por eso no se convierten.
    """
    raw = (raw or "").strip()
    return int(raw) if raw.isdigit() else None


def load_verdicts(paths) -> dict:
    """`{location_id: LocationVerdicts}` leyendo los CSV en orden.

    Un archivo posterior pisa al anterior sobre el mismo fragmento: así
    el dictamen manual sustituye al automático sin editar su archivo.
    """
    by_location: dict = {}
    for path in paths:
        source = Path(path).name
        with Path(path).open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            is_layers = "state_proposed" in (reader.fieldnames or [])
            for row in reader:
                location_id = int(row["location_id"])
                entry = by_location.setdefault(
                    location_id, LocationVerdicts())
                if is_layers:
                    entry.layers = LayerVerdict(
                        ids={layer: _as_id(row.get(f"{layer}_id"))
                             for layer in STATE_LAYERS},
                        source=source)
                    continue
                verdict = FragmentVerdict(
                    value=row["legacy_value"],
                    verdict=row["verdict"].strip(),
                    candidate_id=_as_id(row.get("candidate_id")),
                    source=source)
                entry.fragments[normalize(verdict.value)] = verdict
    return by_location


def rewrite_comments(comments: str, dropped: set) -> str | None:
    """El comentario sin los fragmentos atendidos.

    Reconstruye la línea `YEEKO:` con lo que quedó y conserva intacto lo
    que un editor escribió después; si no queda ningún fragmento, la
    línea desaparece y solo sobrevive ese texto humano. Devuelve `None`
    cuando no queda nada, que es lo que el modelo guarda como vacío.
    """
    body = comments[len(PREFIX):]
    _, separator, tail = body.partition("\n")
    kept = [fragment.verbatim
            for fragment in parse_yeeko_fragments(comments)
            if fragment.verbatim not in dropped]
    if kept:
        return f"{PREFIX} " + "; ".join(kept) + separator + tail
    human = (separator + tail).lstrip("\n")
    return human or None


def append_detail(details: str | None, value: str) -> str:
    return (details + "\n" if details else "") + DETAILS_LABEL + value


class VerdictApplier:
    """Aplica los dictámenes sobre el objeto en memoria y lleva la cuenta.

    Devuelve, por campo del respaldo, qué archivo lo tocó: es lo que le
    permite al CSV de cambios decir de dónde salió cada escritura.
    """

    def __init__(self, by_location: dict):
        self.by_location = by_location
        self.counts: dict = {}

    def count(self, source: str, name: str, amount: int = 1) -> None:
        self.counts.setdefault(source, Counter())[name] += amount

    def apply(self, location) -> dict:
        entry = self.by_location.get(location.pk)
        if not entry:
            return {}
        fragments = {normalize(item.value): item
                     for item in parse_yeeko_fragments(location.comments)}
        sources: dict = {}
        # `verbatim -> archivo que lo atendió`: el CSV de cambios tiene
        # que poder decir de dónde salió la reescritura del comentario.
        dropped: dict = {}
        if entry.layers:
            self._apply_layers(
                location, entry.layers, fragments, dropped, sources)
        for key, verdict in entry.fragments.items():
            fragment = fragments.get(key)
            if fragment is None:
                # El comentario ya no trae ese fragmento: el CSV quedó
                # atrás de la base y aplicarlo a ciegas sería inventar.
                self.count(verdict.source, "fragmento_ausente")
                continue
            self._apply_fragment(
                location, verdict, fragment, dropped, sources)
        if dropped:
            self._rewrite(location, dropped, sources)
        return sources

    def _apply_layers(self, location, layers, fragments, dropped,
                      sources) -> None:
        """Llena las capas que el revisor resolvió y borra sus fragmentos.

        Cada capa se atiende por separado: el CSV puede traer estado y
        municipio sin localidad, y entonces el fragmento de localidad se
        queda esperando a que lo resuelva el motor o un humano.
        """
        source = layers.source
        for layer in STATE_LAYERS:
            candidate_id = layers.ids.get(layer)
            if not candidate_id:
                continue
            current = getattr(location, f"{layer}_id")
            if current is None:
                self._set(location, layer, candidate_id, source, sources)
                self.count(source, f"llenar_{layer}")
            elif current != candidate_id:
                self.count(source, "llenar_en_conflicto")
                continue
            else:
                self.count(source, "llenar_ya_capturado")
            for fragment in fragments.values():
                if LAYER_BY_KIND.get(fragment.kind) == layer:
                    dropped[fragment.verbatim] = source
                    self.count(source, "fragmentos_borrados")

    def _apply_fragment(self, location, verdict, fragment, dropped,
                        sources) -> None:
        source = verdict.source
        if verdict.verdict in KEEP:
            self.count(source, "sin_cambio")
            return
        layer = (LAYER_BY_KIND.get(fragment.kind)
                 or LAYER_BY_TEMPLATE.get(fragment.template))
        if verdict.verdict == FILL:
            if not self._fill(location, layer, verdict, sources):
                return
        elif verdict.verdict == TO_DETAILS:
            self._to_details(location, verdict, sources)
        elif verdict.verdict == EMPTY:
            self._set(location, layer, None, source, sources)
            self.count(source, "vaciar")
        elif verdict.verdict == USELESS:
            self.count(source, "inutil")
        else:
            self.count(source, f"veredicto_desconocido:{verdict.verdict}")
            return
        dropped[fragment.verbatim] = source
        self.count(source, "fragmentos_borrados")

    def _fill(self, location, layer, verdict, sources) -> bool:
        """`True` si el fragmento ya puede borrarse del comentario.

        Se llena solo lo vacío, como en el motor. Si el campo trae otro
        id, el fragmento se queda: el comentario es la única constancia
        de que el nombre legado y lo capturado no coinciden.
        """
        source = verdict.source
        if not layer or not verdict.candidate_id:
            self.count(source, "llenar_sin_candidato")
            return False
        current = getattr(location, f"{layer}_id")
        if current is None:
            self._set(location, layer, verdict.candidate_id, source, sources)
            self.count(source, f"llenar_{layer}")
            return True
        if current == verdict.candidate_id:
            self.count(source, "llenar_ya_capturado")
            return True
        self.count(source, "llenar_en_conflicto")
        return False

    def _to_details(self, location, verdict, sources) -> None:
        source = verdict.source
        value = normalize(verdict.value)
        if value and value in normalize(location.details):
            self.count(source, "details_duplicado")
            return
        location.details = append_detail(location.details, verdict.value)
        self.count(source, "details_agregado")
        self._mark("details", source, sources)

    def _rewrite(self, location, dropped, sources) -> None:
        rewritten = rewrite_comments(location.comments, set(dropped))
        if rewritten == location.comments:
            return
        location.comments = rewritten
        contributors = sorted(set(dropped.values()))
        self._mark("comments", "|".join(contributors), sources)
        if rewritten is None:
            for source in contributors:
                self.count(source, "comentarios_vaciados")

    @staticmethod
    def _mark(name: str, source: str, sources: dict) -> None:
        previous = sources.get(name)
        if previous and source not in previous.split("|"):
            source = previous + "|" + source
        sources[name] = source

    def _set(self, location, layer, value, source, sources) -> None:
        setattr(location, f"{layer}_id", value)
        self._mark(f"{layer}_id", source, sources)
