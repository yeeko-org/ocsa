"""Marca para revisión editorial, en el dashboard, lo que no cuadra.

Dos clases de ubicación, recomputadas de los datos en cada corrida:

- `far_pin`: puntos con proyecto cuyo pin está a más de dos kilómetros
  del municipio capturado o fuera del estado capturado
  (`space_time/far_pins.py`).
- `legacy_name`: las dos ubicaciones cuyo nombre de localidad del legado
  no tiene resolución posible. Van por id porque cada una es un
  veredicto humano individual, como `HUMAN_VERDICTS` del backfill.

En las dos clases se agrega un comentario fechado y firmado, con la
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

from space_time.far_pins import THRESHOLD_KM, name_of, scan
from space_time.models import Location

AUTHOR = "Ricardo"
APPROVED = "finished"
FLAGGED = "approved_with_notes"
SEPARATOR = "\n\n"
UPDATED_FIELDS = ["status_location", "comments"]
DEFAULT_OUT = ".claude/review_flags_{day}.csv"
CSV_FIELDS = ("location_id", "project_id", "project", "reason",
              "status_before", "status_after", "comment")
FAR_PIN = "far_pin"
LEGACY_NAME = "legacy_name"
BATCH_SIZE = 500

# Localidades del legado sin resolución posible: el nombre capturado
# tiene más de una candidata y no hay dato que desempate. Van por id
# porque son dictámenes humanos, no una regla.
LEGACY_UNRESOLVED = {
    12302: ("Loreto",
            "en Chínipas hay dos candidatas, «Ignacio Valenzuela Lagarda "
            "(Loreto)» y «Los Alamillos de Loreto», y la capturada es la "
            "segunda"),
    12643: ("Los Napuchis",
            "en Carichí hay siete localidades homónimas"),
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
    """Qué se le dice al editor sobre un pin lejano, según por qué salió."""
    parts = []
    if pin.far_municipality:
        parts.append(
            f"el pin está a {pin.to_municipality:.1f} km del municipio "
            f"capturado ({name_of(pin.location.municipality)}); revisar "
            f"coordenada o municipio.")
    if pin.far_state:
        computed = name_of(getattr(pin.resolution, "state", None))
        captured = name_of(pin.location.state)
        parts.append(
            f"El pin cae en {computed}, no en {captured}."
            if computed else
            f"El pin no cae dentro de ningún estado; el capturado es "
            f"{captured}.")
    return " ".join(parts)


def legacy_text(name: str, reason: str) -> str:
    return (f"la localidad del legado «{name}» no se pudo resolver: "
            f"{reason}; revisar.")


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


def select(threshold: float = THRESHOLD_KM) -> tuple[dict, int, list[int]]:
    """Recomputa la selección desde los datos.

    Devuelve las entradas por id, cuántos puntos se revisaron y los ids
    dictaminados que ya no existen en la base.
    """
    entries: dict[int, Entry] = {}
    found, seen = scan(threshold)
    for pin in found:
        entry = entries.setdefault(pin.location.pk, Entry(pin.location))
        entry.add(FAR_PIN, far_pin_text(pin))
    missing = []
    for pk, (name, reason) in sorted(LEGACY_UNRESOLVED.items()):
        entry = entries.get(pk)
        if entry is None:
            location = (Location.objects
                        .select_related("project", "municipality", "state")
                        .filter(pk=pk).first())
            if location is None:
                missing.append(pk)
                continue
            entry = entries.setdefault(pk, Entry(location))
        entry.add(LEGACY_NAME, legacy_text(name, reason))
    return entries, seen, missing


class Flagger:
    """Aplica (o simula) las marcas y deja el CSV de lo que cambiaría."""

    def __init__(self, apply: bool, out: str, threshold: float = THRESHOLD_KM,
                 day: date | None = None, expect: int | None = None):
        self.apply = apply
        self.out = Path(out)
        self.threshold = threshold
        self.day = day or date.today()
        self.expect = expect
        self.deviation = ""
        self.seen = 0
        self.missing: list[int] = []
        self.counts: dict[str, dict[str, int]] = {}
        self.rows: list[dict] = []
        self.pending: list[Location] = []

    def run(self) -> list[str]:
        entries, self.seen, self.missing = select(self.threshold)
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
        # aunque cambie la fecha de la firma.
        fresh = [(reason, text) for reason, text in entry.texts
                 if text not in (location.comments or "")]
        if not fresh:
            for reason in entry.reasons:
                self.count(reason, "ya_marcada")
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
            f"Puntos con proyecto y coordenadas revisados: {self.seen}",
            f"Umbral: {self.threshold} km",
            f"{prefix}Ubicaciones marcadas: {len(self.pending)} "
            f"({len(self.rows)} comentarios; {changed} cambian de estatus)",
        ]
        for reason in sorted(self.counts):
            buckets = self.counts[reason]
            lines.append(
                f"  {reason}: estatus {buckets['estatus']}, "
                f"solo comentario {buckets['solo_comentario']}, "
                f"ya marcadas {buckets['ya_marcada']}")
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
