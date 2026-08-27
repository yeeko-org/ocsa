"""Piezas comunes a los cargadores de catálogos del AGEEML.

Django ignora los módulos de `management/commands` cuyo nombre empieza
con guion bajo, así que el código compartido puede vivir junto a sus
comandos sin que `manage.py` lo tome por uno.
"""

import csv

from django.core.management.base import BaseCommand

# Los ZIP del AGEEML traen una variante ANSI y otra UTF-8; el script de
# descarga se queda con la ANSI (ver `geo_files/README.md`).
CSV_ENCODING = "latin1"


def integer_or_none(value: str | None) -> int | None:
    """Las columnas numéricas del AGEEML vienen vacías en algunas filas."""
    return int(value) if (value or "").strip().isdigit() else None


class LoaderCommand(BaseCommand):
    """Comando de un solo `--dry-run` que delega en `loader_class`."""

    loader_class = None
    dry_run_help = "Solo reporta lo que haría, sin escribir"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help=self.dry_run_help)

    def handle(self, *args, **options):
        loader = self.loader_class(dry_run=options["dry_run"])
        for line in loader.report():
            self.stdout.write(line)


class CsvLoader:
    """Recorre un catálogo del AGEEML acumulando los errores por fila.

    Una fila rota no aborta la carga: el catálogo trae decenas de miles
    de renglones y conviene terminar y reportar al final.
    """

    csv_path = ""
    # Cómo se nombra la fila en el mensaje de error y con qué columna se
    # identifica: «Error en el municipio 001: ...».
    row_label = ""
    row_key = ""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.created = 0
        self.updated = 0
        self.errors: list[str] = []

    @property
    def prefix(self) -> str:
        return "[dry-run] " if self.dry_run else ""

    def load_csv(self) -> None:
        with open(self.csv_path, newline="", encoding=CSV_ENCODING) as file:
            for row in csv.DictReader(file):
                try:
                    self.read_row(row)
                except Exception as error:
                    self.errors.append(
                        f"Error en {self.row_label} "
                        f"{row.get(self.row_key)}: {error}")

    def read_row(self, row: dict) -> None:
        raise NotImplementedError

    def report_counts(self) -> list[str]:
        raise NotImplementedError

    def report(self) -> list[str]:
        return self.report_counts() + self.errors
