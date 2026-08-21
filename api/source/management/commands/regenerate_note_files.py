"""Regenera o rellena los adjuntos de nota de task-42.

Dos universos disjuntos:

``reforma``
    Notas de Reforma cuyo único adjunto no vacío es el autogenerado que
    en realidad es la portada de sección. Se regeneran con
    ``replace=True``: se borra el NoteFile viejo y se corrige
    ``Note.pages``. Las notas con algún adjunto cargado a mano quedan
    fuera aunque también tengan el autogenerado.

``backfill``
    Notas sin ningún NoteFile cuya fuente tenga generador registrado
    (Reforma y La Jornada). Se genera sin ``replace``. Proceso no tiene
    generador: sus adjuntos se cargan a mano.
"""

import os
import re
from typing import Iterable

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import QuerySet

from source.attachment import generate_attachment, get_attachment_generator
from source.models import Article, Note

# Nombre del PDF que produjo la generación vieja de Reforma: código de
# página de la hemeroteca. El sufijo libre cubre las colisiones que
# renombró Django (``_L9uApPx``) y los duplicados manuales (``-2``).
AUTO_NAME = re.compile(r"^R[A-Z]{2,5}\d{8}[-_].*$", re.IGNORECASE)

MODES = ("reforma", "backfill", "all")


class Command(BaseCommand):
    """Regenera los PDF erróneos de Reforma y rellena notas sin adjunto."""

    help = __doc__

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--mode", choices=MODES, default="all",
            help="Universo a procesar (default: all).")
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Procesa a lo más N notas por modo.")
        parser.add_argument(
            "--ids", type=str, default=None,
            help="Lista de pk de Note separadas por coma.")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Solo lista qué haría; no descarga ni escribe.")

    def handle(self, *args, **options) -> None:
        mode: str = options["mode"]
        limit: int | None = options["limit"]
        dry_run: bool = options["dry_run"]
        only_ids = self.parse_ids(options["ids"])

        totals: dict[str, int] = {}
        if mode in ("reforma", "all"):
            notes = self.reforma_notes(only_ids)
            totals["reforma"] = self.run_mode(
                "reforma", notes, replace=True, limit=limit, dry_run=dry_run)
        if mode in ("backfill", "all"):
            notes = self.backfill_notes(only_ids)
            totals["backfill"] = self.run_mode(
                "backfill", notes, replace=False, limit=limit,
                dry_run=dry_run)

        self.stdout.write("")
        for name, count in totals.items():
            self.stdout.write(f"[{name}] notas candidatas: {count}")

    @staticmethod
    def parse_ids(raw: str | None) -> list[int] | None:
        if not raw:
            return None
        return [int(part) for part in raw.split(",") if part.strip()]

    # ------------------------------------------------------------------
    # Selección de universos

    @staticmethod
    def base_queryset(only_ids: list[int] | None) -> QuerySet[Note]:
        notes = Note.objects.select_related("source").prefetch_related(
            "files", "articles")
        if only_ids is not None:
            notes = notes.filter(pk__in=only_ids)
        return notes

    def reforma_notes(self, only_ids: list[int] | None) -> list[Note]:
        notes = self.base_queryset(only_ids).filter(
            source__main_url__icontains="reforma.com")
        selected = []
        for note in notes:
            names = self.file_names(note)
            # Un solo adjunto no autogenerado basta para excluir la nota:
            # es carga manual del equipo y no se toca.
            if names and all(AUTO_NAME.match(name) for name in names):
                selected.append(note)
        return selected

    def backfill_notes(self, only_ids: list[int] | None) -> list[Note]:
        notes = self.base_queryset(only_ids)
        return [
            note for note in notes
            if not self.file_names(note)
            and get_attachment_generator(note.source) is not None
        ]

    @staticmethod
    def file_names(note: Note) -> list[str]:
        return [
            os.path.basename(note_file.file.name)
            for note_file in note.files.all()
            if note_file.file and note_file.file.name
        ]

    # ------------------------------------------------------------------
    # Ejecución

    def run_mode(
            self, name: str, notes: Iterable[Note], replace: bool,
            limit: int | None, dry_run: bool,
    ) -> int:
        notes = list(notes)
        total = len(notes)
        if limit is not None:
            notes = notes[:limit]

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"== {name}: {total} candidatas, se procesan {len(notes)} =="))

        counts = {"ok": 0, "sin_article": 0, "sin_adjunto": 0, "error": 0}
        for note in notes:
            status, detail = self.process(note, replace, dry_run)
            counts[status] = counts.get(status, 0) + 1
            self.report(note, name, status, detail)

        self.stdout.write(
            f"-- {name}: " + ", ".join(
                f"{key}={value}" for key, value in counts.items()))
        return total

    def process(
            self, note: Note, replace: bool, dry_run: bool,
    ) -> tuple[str, str]:
        article = self.pick_article(note)
        if article is None:
            return "sin_article", "la nota no tiene Article asociado"
        if dry_run:
            return "ok", f"article={article.pk} uid={article.uid}"

        try:
            note_file = generate_attachment(
                article, note=note, replace=replace)
        except Exception as error:  # noqa: BLE001 — se reporta tal cual
            return "error", f"{type(error).__name__}: {error}"

        if note_file is None:
            return "sin_adjunto", (
                "el generador devolvió None (metadatos o PDF inaccesible)")
        note.refresh_from_db(fields=["pages"])
        return "ok", f"file={note_file.file.name} pages={note.pages}"

    @staticmethod
    def pick_article(note: Note) -> Article | None:
        articles = list(note.articles.all())
        if not articles:
            return None
        # Con varios artículos ligados, el más reciente es el que trae los
        # metadatos de página que task-41 empezó a guardar.
        return sorted(articles, key=lambda item: item.pk)[-1]

    def report(
            self, note: Note, mode: str, status: str, detail: str,
    ) -> None:
        line = (
            f"nota={note.pk} fuente={note.source.name} modo={mode} "
            f"estado={status} :: {detail}")
        if status == "ok":
            self.stdout.write(self.style.SUCCESS(line))
        elif status == "error":
            self.stdout.write(self.style.ERROR(line))
        else:
            self.stdout.write(self.style.WARNING(line))
