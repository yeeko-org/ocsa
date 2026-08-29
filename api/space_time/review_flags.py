"""Marca para revisión editorial, en el dashboard, lo que no cuadra.

Nueve clases de ubicación, recomputadas de los datos en cada corrida:

- `far_pin`: puntos con proyecto cuyo pin está a más de `--threshold`
  del municipio capturado o fuera del estado capturado
  (`space_time/far_pins.py`).
- `far_pin_locality`: puntos cuyo pin está a más de `--locality-threshold`
  de la localidad capturada (`space_time/far_pins.py`).
- `trace_off_municipality`: líneas y polígonos cuyo trazo no toca el
  polígono del municipio capturado (`space_time/off_traces.py`).
- `trace_off_state`: líneas y polígonos cuyo trazo no toca el polígono
  del estado capturado; no exige municipio capturado, y por eso es la
  única que alcanza a los trazos sin él (`space_time/off_traces.py`).
- `trace_in_other_state`: líneas y polígonos que atraviesan municipios de
  un estado ajeno al capturado, aunque no se hayan salido del suyo
  (`space_time/off_traces.py`).
- `base_off_crossed`: líneas y polígonos cuyo municipio capturado no
  está entre los que el motor da por atravesados
  (`space_time/off_traces.py`).
- `trace_off_locality`: líneas y polígonos cuyo trazo está a más de
  `--locality-threshold` de la localidad capturada
  (`space_time/off_traces.py`).
- `state_mismatch`: el estado capturado no es el del municipio capturado
  (`space_time/state_mismatch.py`).
- `legacy_name`: las dos ubicaciones cuyo nombre de localidad del legado
  no tiene resolución posible. Van por id porque cada una es un
  veredicto humano individual, como `HUMAN_VERDICTS` del backfill.

Una misma ubicación puede salir por varias clases: cada razón agrega su
propio comentario y su propia fila del CSV, pero el estatus se mueve una
sola vez.

En todas las clases se agrega un comentario fechado y firmado, con la
convención del front (`\\n\\n` + `DD/MM/YYYY - Nombre: texto`), porque el
estatus solo no dice por qué. El estatus se mueve a «Aprobado (con
observaciones)» únicamente cuando estaba en «Aprobado»: en cualquier
otro estatus la ubicación ya está en flujo de revisión y moverla la
sacaría de él.

Nunca llama a `Location.save()`: ese método recalcula el
`status_location` derivado del proyecto y aquí sí se mueven estatus, así
que el efecto colateral sería sobre otra entidad. Escribe con
`bulk_update`, dentro de una transacción.
"""

import csv
from datetime import date
from pathlib import Path

from django.core.management.base import CommandError
from django.db import transaction

from space_time.far_pins import (
    LOCALITY_THRESHOLD_KM, THRESHOLD_KM, name_of, scan,
    scan_localities as scan_locality_pins)
from space_time.models import Location
from space_time.off_traces import (
    scan as scan_traces, scan_base_municipality, scan_in_other_state,
    scan_localities as scan_trace_localities,
    scan_states as scan_trace_states)
from space_time.state_mismatch import scan as scan_states

AUTHOR = "Ricardo"
APPROVED = "finished"
FLAGGED = "approved_with_notes"
SEPARATOR = "\n\n"
UPDATED_FIELDS = ["status_location", "comments"]
DEFAULT_OUT = ".claude/review_flags_{day}.csv"
CSV_FIELDS = ("location_id", "project_id", "project", "reason",
              "status_before", "status_after", "comment")
FAR_PIN = "far_pin"
FAR_PIN_LOCALITY = "far_pin_locality"
TRACE_OFF_MUNICIPALITY = "trace_off_municipality"
TRACE_OFF_STATE = "trace_off_state"
TRACE_IN_OTHER_STATE = "trace_in_other_state"
BASE_OFF_CROSSED = "base_off_crossed"
TRACE_OFF_LOCALITY = "trace_off_locality"
STATE_MISMATCH = "state_mismatch"
LEGACY_NAME = "legacy_name"
BATCH_SIZE = 500

# Localidades del legado sin resolución posible: el nombre capturado
# tiene más de una candidata en su municipio y no hay dato que desempate.
# Van por id porque son dictámenes humanos, no una regla.
LEGACY_UNRESOLVED = {
    # Chínipas: «Ignacio Valenzuela Lagarda (Loreto)» y «Los Alamillos
    # de Loreto».
    12302: ("Loreto", 2),
    12643: ("Los Napuchis", 7),
}


def signed(text: str, day: date | None = None) -> str:
    """Comentario con la convención del front: fecha, autor y texto."""
    day = day or date.today()
    return f"{day.strftime('%d/%m/%Y')} - {AUTHOR}: {text}"


def append_comment(comments: str | None, line: str) -> str:
    """Agrega el comentario al final, sin tocar lo que ya estaba."""
    if not comments:
        return line
    return comments + SEPARATOR + line


def strip_comment(comments: str | None, line: str) -> str | None:
    """Quita el comentario agregado y su separador; `None` si no queda nada."""
    if not comments:
        return comments
    remaining = comments.replace(SEPARATOR + line, "").replace(line, "")
    return remaining.strip(SEPARATOR) or None


def far_pin_text(pin) -> str:
    """Qué se le dice al editor sobre un pin lejano, según por qué salió.

    El estado y el municipio calculados no se nombran: el dashboard ya
    los muestra en la tarjeta de municipios, y repetirlos en el
    comentario los congela con la fecha de la corrida.
    """
    parts = []
    if pin.far_municipality:
        parts.append(
            f"el pin está a {pin.to_municipality:.1f} km del municipio "
            f"capturado ({name_of(pin.location.municipality)}); revisar "
            f"coordenada o municipio.")
    if pin.far_state:
        parts.append(
            f"El pin no cae dentro del estado capturado "
            f"({name_of(pin.location.state)}); revisar coordenada o "
            f"estado.")
    return " ".join(parts)


def off_trace_text(off) -> str:
    """Qué se le dice al editor sobre un trazo fuera de su municipio.

    Los municipios que sí atraviesa no se enumeran: ya quedan guardados
    en el M2M y el editor los ve en la ficha.
    """
    captured = name_of(off.location.municipality)
    if not off.crossed:
        return (f"el trazo no toca el municipio capturado ({captured}) "
                f"ni ningún otro; revisar trazo o municipio.")
    return f"el trazo no toca el municipio capturado ({captured})."


def off_state_text(off) -> str:
    """Qué se le dice al editor sobre un trazo fuera de su estado.

    Los estados en los que sí cae no se enumeran, igual que los
    municipios de `off_trace_text`: el dashboard ya los muestra.
    """
    return (f"el trazo está a {off.distance:.1f} km del estado capturado "
            f"({name_of(off.location.state)}); revisar trazo o estado.")


def in_other_state_text(off) -> str:
    """Qué se le dice al editor sobre un trazo que desborda su estado.

    Cuántos municipios ajenos atraviesa sí se dice —es la magnitud del
    desborde, y no un dato que la ficha repita—; cuáles son, no.
    """
    count = len(off.crossed)
    municipalities = "un municipio" if count == 1 else f"{count} municipios"
    return (f"el trazo atraviesa {municipalities} de otro estado, además "
            f"del capturado ({name_of(off.location.state)}); revisar trazo "
            f"o estado.")


def base_off_crossed_text(off) -> str:
    """Qué se le dice al editor sobre un municipio base no atravesado."""
    return (f"el municipio capturado ({name_of(off.location.municipality)}) "
            f"no está entre los que el trazo atraviesa.")


def far_locality_text(pin) -> str:
    """Qué se le dice al editor sobre un pin lejos de su localidad."""
    return (f"el pin está a {pin.distance:.1f} km de la localidad "
            f"capturada ({name_of(pin.location.locality)}).")


def off_locality_text(off) -> str:
    """Qué se le dice al editor sobre un trazo lejos de su localidad."""
    return (f"la localidad capturada ({name_of(off.location.locality)}) "
            f"está a {off.distance:.1f} km del trazo.")


def state_mismatch_text(mismatch) -> str:
    """Qué se le dice al editor sobre un estado que no es del municipio."""
    municipality = mismatch.location.municipality
    return (f"el estado capturado ({name_of(mismatch.location.state)}) no "
            f"es el del municipio ({name_of(municipality)}, en "
            f"{name_of(municipality.state)}).")


def legacy_text(name: str, candidates: int) -> str:
    return (f"la localidad del legado «{name}» tiene {candidates} "
            f"candidatas en el catálogo; revisar.")


class Entry:
    """Una ubicación seleccionada con los comentarios que le tocan."""

    def __init__(self, location):
        self.location = location
        self.texts: list[tuple[str, str]] = []

    def add(self, reason: str, text: str) -> None:
        self.texts.append((reason, text))

    @property
    def reasons(self) -> list[str]:
        return sorted({reason for reason, _ in self.texts})


def select(threshold: float = THRESHOLD_KM,
           locality_threshold: float | None = None
           ) -> tuple[dict, dict, list[int]]:
    """Recomputa la selección desde los datos.

    Devuelve las entradas por id, cuántas ubicaciones se revisaron de
    cada clase medible y los ids dictaminados que ya no existen.
    """
    if locality_threshold is None:
        locality_threshold = LOCALITY_THRESHOLD_KM
    entries: dict[int, Entry] = {}

    def entry_for(location) -> Entry:
        return entries.setdefault(location.pk, Entry(location))

    found, seen_pins = scan(threshold)
    for pin in found:
        entry_for(pin.location).add(FAR_PIN, far_pin_text(pin))
    locality_pins, locality_seen = scan_locality_pins(locality_threshold)
    for pin in locality_pins:
        entry_for(pin.location).add(FAR_PIN_LOCALITY, far_locality_text(pin))
    off_traces, seen_traces = scan_traces()
    for off in off_traces:
        entry_for(off.location).add(
            TRACE_OFF_MUNICIPALITY, off_trace_text(off))
    off_states, seen_trace_states = scan_trace_states()
    for off in off_states:
        entry_for(off.location).add(TRACE_OFF_STATE, off_state_text(off))
    in_other, seen_in_other = scan_in_other_state()
    for off in in_other:
        entry_for(off.location).add(
            TRACE_IN_OTHER_STATE, in_other_state_text(off))
    base_off, seen_base = scan_base_municipality()
    for off in base_off:
        entry_for(off.location).add(
            BASE_OFF_CROSSED, base_off_crossed_text(off))
    off_localities, trace_locality_seen = scan_trace_localities(
        locality_threshold)
    for off in off_localities:
        entry_for(off.location).add(TRACE_OFF_LOCALITY, off_locality_text(off))
    mismatches, seen_states = scan_states()
    for mismatch in mismatches:
        entry_for(mismatch.location).add(
            STATE_MISMATCH, state_mismatch_text(mismatch))
    seen = {
        "pins": seen_pins,
        "traces": seen_traces,
        "trace_states": seen_trace_states,
        "in_other_state": seen_in_other,
        "base_municipality": seen_base,
        "locality_pins": locality_seen["seen"],
        "locality_polygon": locality_seen["polygon"],
        "locality_point": locality_seen["point"],
        "locality_unmeasurable": locality_seen["unmeasurable"],
        "trace_localities": trace_locality_seen["seen"],
        "trace_locality_polygon": trace_locality_seen["polygon"],
        "trace_locality_point": trace_locality_seen["point"],
        "locality_unmeasurable_traces": trace_locality_seen["unmeasurable"],
        "states": seen_states,
    }
    missing = []
    for pk, (name, candidates) in sorted(LEGACY_UNRESOLVED.items()):
        entry = entries.get(pk)
        if entry is None:
            location = (Location.objects
                        .select_related("project", "municipality", "state")
                        .filter(pk=pk).first())
            if location is None:
                missing.append(pk)
                continue
            entry = entries.setdefault(pk, Entry(location))
        entry.add(LEGACY_NAME, legacy_text(name, candidates))
    return entries, seen, missing


class Flagger:
    """Aplica (o simula) las marcas y deja el CSV de lo que cambiaría."""

    def __init__(self, apply: bool, out: str, threshold: float = THRESHOLD_KM,
                 day: date | None = None, expect: int | None = None,
                 locality_threshold: float | None = None):
        self.apply = apply
        self.out = Path(out)
        self.threshold = threshold
        self.locality_threshold = (LOCALITY_THRESHOLD_KM
                                   if locality_threshold is None
                                   else locality_threshold)
        self.day = day or date.today()
        self.expect = expect
        self.deviation = ""
        self.seen: dict[str, int] = {}
        self.missing: list[int] = []
        self.counts: dict[str, dict[str, int]] = {}
        self.rows: list[dict] = []
        self.pending: list[Location] = []

    def run(self) -> list[str]:
        entries, self.seen, self.missing = select(
            self.threshold, self.locality_threshold)
        for pk in sorted(entries):
            self.flag(entries[pk])
        # Antes de escribir: la guarda no sirve si la desviación se
        # descubre con los estatus ya movidos.
        self.deviation = check_expected(len(self.pending), self.expect)
        # El CSV es lo único con lo que --revert deshace la corrida: va
        # antes del bulk_update, como el respaldo del backfill.
        self.write_csv()
        if self.apply and self.pending:
            with transaction.atomic():
                Location.objects.bulk_update(
                    self.pending, UPDATED_FIELDS, batch_size=BATCH_SIZE)
        return self.report()

    def count(self, reason: str, bucket: str) -> None:
        self.counts.setdefault(
            reason, {"estatus": 0, "solo_comentario": 0, "ya_marcada": 0})
        self.counts[reason][bucket] += 1

    def flag(self, entry: Entry) -> None:
        location = entry.location
        status_before = location.status_location_id
        # El texto ya presente no se repite: la corrida es idempotente
        # aunque cambie la fecha de la firma. La cuenta va por razón y no
        # por entrada: una ubicación puede traer una razón ya comentada y
        # otra nueva, y cada una cuenta en su propio renglón.
        comments = location.comments or ""
        fresh, marked = [], set()
        for reason, text in entry.texts:
            if text in comments:
                marked.add(reason)
            else:
                fresh.append((reason, text))
        for reason in sorted(marked):
            self.count(reason, "ya_marcada")
        if not fresh:
            return
        status_after = (FLAGGED if status_before == APPROVED
                        else status_before)
        for reason, text in fresh:
            line = signed(text, self.day)
            location.comments = append_comment(location.comments, line)
            self.count(reason,
                       "estatus" if status_after != status_before
                       else "solo_comentario")
            self.rows.append({
                "location_id": location.pk,
                "project_id": location.project_id,
                "project": str(location.project or ""),
                "reason": reason,
                "status_before": status_before or "",
                "status_after": status_after or "",
                "comment": line,
            })
        location.status_location_id = status_after
        self.pending.append(location)

    def write_csv(self) -> None:
        if not self.rows:
            return
        self.out.parent.mkdir(parents=True, exist_ok=True)
        with self.out.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(self.rows)

    def report(self) -> list[str]:
        prefix = "" if self.apply else "[simulación] "
        # Por ubicación y no por fila: una misma ubicación puede llevar
        # dos comentarios y mueve el estatus una sola vez.
        changed = len({row["location_id"] for row in self.rows
                       if row["status_before"] != row["status_after"]})
        lines = [
            f"Puntos con proyecto y coordenadas revisados: "
            f"{self.seen.get('pins', 0)}",
            f"Trazos con municipio capturado revisados: "
            f"{self.seen.get('traces', 0)} "
            f"({self.seen.get('base_municipality', 0)} también contra los "
            f"municipios atravesados)",
            f"Trazos con estado capturado revisados: "
            f"{self.seen.get('trace_states', 0)} "
            f"({self.seen.get('in_other_state', 0)} también contra los "
            f"estados de los municipios atravesados)",
            f"Puntos con localidad capturada revisados: "
            f"{self.seen.get('locality_pins', 0)} "
            f"({self.seen.get('locality_polygon', 0)} medidos contra "
            f"polígono, {self.seen.get('locality_point', 0)} contra el "
            f"punto del catálogo)",
            f"Trazos con localidad capturada revisados: "
            f"{self.seen.get('trace_localities', 0)} "
            f"({self.seen.get('trace_locality_polygon', 0)} medidos contra "
            f"polígono, {self.seen.get('trace_locality_point', 0)} contra "
            f"el punto del catálogo)",
            f"Ubicaciones con estado y municipio capturados revisadas: "
            f"{self.seen.get('states', 0)}",
            f"Umbral: {self.threshold} km "
            f"(localidad: {self.locality_threshold} km)",
            f"{prefix}Ubicaciones marcadas: {len(self.pending)} "
            f"({len(self.rows)} comentarios; {changed} cambian de estatus)",
        ]
        for reason in sorted(self.counts):
            buckets = self.counts[reason]
            lines.append(
                f"  {reason}: estatus {buckets['estatus']}, "
                f"solo comentario {buckets['solo_comentario']}, "
                f"ya marcadas {buckets['ya_marcada']}")
        unmeasurable = (self.seen.get("locality_unmeasurable", 0)
                        + self.seen.get("locality_unmeasurable_traces", 0))
        if unmeasurable:
            lines.append(
                f"Localidades capturadas sin polígono ni coordenadas (no "
                f"medibles): {unmeasurable}")
        if self.deviation:
            lines.append(self.deviation)
        if self.missing:
            lines.append(f"Dictámenes sin ubicación en la base: "
                         f"{self.missing}")
        lines.append(f"CSV: {self.out}" if self.rows
                     else "Nada que marcar: no hay CSV")
        if not self.apply:
            lines.append("No se escribió nada. Repite con --apply.")
        return lines


class Reverter:
    """Deshace una corrida desde su CSV: estatus previo y sin el texto."""

    def __init__(self, source: str):
        self.source = Path(source)
        self.restored = 0
        self.missing = 0
        self.drifted = 0

    def run(self) -> list[str]:
        by_id: dict[int, list[dict]] = {}
        for row in self.read():
            by_id.setdefault(int(row["location_id"]), []).append(row)
        ids = sorted(by_id)
        rows = list(Location.objects.filter(pk__in=ids))
        for location in rows:
            expected = by_id[location.pk][0]["status_after"] or None
            if location.status_location_id != expected:
                self.drifted += 1
            for row in by_id[location.pk]:
                location.comments = strip_comment(
                    location.comments, row["comment"])
            location.status_location_id = (
                by_id[location.pk][0]["status_before"] or None)
        with transaction.atomic():
            Location.objects.bulk_update(
                rows, UPDATED_FIELDS, batch_size=BATCH_SIZE)
        self.restored = len(rows)
        self.missing = len(ids) - self.restored
        return self.report()

    def read(self) -> list[dict]:
        try:
            with self.source.open(encoding="utf-8-sig") as handle:
                return list(csv.DictReader(handle))
        except OSError as error:
            raise CommandError(
                f"No se pudo leer el CSV {self.source}: {error}") from error

    def report(self) -> list[str]:
        lines = [
            f"CSV: {self.source}",
            f"Ubicaciones restauradas: {self.restored}",
        ]
        if self.missing:
            lines.append(f"Ya no existen en la base: {self.missing}")
        if self.drifted:
            lines.append(
                f"Editadas después de la marca (se restauraron igual): "
                f"{self.drifted}")
        return lines


def check_expected(count: int, expected: int | None) -> str:
    """Aborta si la selección se desvía más del 5 % de lo esperado."""
    if expected is None:
        return ""
    deviation = abs(count - expected) / expected if expected else 1
    if deviation > 0.05:
        raise CommandError(
            f"La selección ({count}) se desvía {deviation:.1%} de lo "
            f"esperado ({expected}); revisa antes de escribir.")
    return f"Desviación contra --expect {expected}: {deviation:.1%}."
