"""Comando de revisión y backfill de la geolocalización.

Solo lee argumentos: las tres pasadas viven en `space_time/backfill.py`,
porque el respaldo y los dictámenes también los usan los tests y los
diagnósticos, que no pasan por el comando.
"""

from datetime import date

from django.core.management.base import BaseCommand

from space_time.backfill import (
    DEFAULT_BACKUP, DEFAULT_CHANGES, DEFAULT_OUT, Filler, Reverter, Reviewer)


class Command(BaseCommand):
    help = "Revisa o rellena la geolocalización derivada de las ubicaciones"

    def add_arguments(self, parser):
        parser.add_argument(
            "--review", action="store_true",
            help="Compara lo capturado con lo calculado y escribe el CSV")
        parser.add_argument(
            "--fill", action="store_true",
            help="Llena lo vacío y recalcula los campos derivados")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Con --fill, cuenta lo que llenaría sin escribir")
        parser.add_argument(
            "--out", default=DEFAULT_OUT,
            help=f"Ruta del CSV de revisión (default: {DEFAULT_OUT})")
        parser.add_argument(
            "--limit", type=int,
            help="Acota el universo, para probar el comando")
        parser.add_argument(
            "--backup", default="",
            help="Ruta del respaldo que escribe --fill (default: "
                 + DEFAULT_BACKUP.format(day="<fecha>") + ")")
        parser.add_argument(
            "--revert", default="",
            help="Restaura los valores previos de un respaldo de --fill")
        parser.add_argument(
            "--verdicts", nargs="+", default=[],
            help="CSV de dictámenes por ubicación, en orden de prioridad: "
                 "el último gana sobre el mismo fragmento")
        parser.add_argument(
            "--changes-out", default="",
            help="CSV con lo que la pasada cambiaría, campo por campo "
                 "(default: " + DEFAULT_CHANGES.format(day="<fecha>") + ")")

    def handle(self, *args, **options):
        if options["revert"]:
            for line in Reverter(options["revert"]).run():
                self.stdout.write(line)
            return
        if not options["review"] and not options["fill"]:
            self.stdout.write(
                "Nada que hacer: elige --review, --fill o --revert.")
            return
        if options["review"]:
            for line in Reviewer(options["out"], options["limit"]).run():
                self.stdout.write(line)
        if options["fill"]:
            day = date.today().isoformat()
            backup = options["backup"] or DEFAULT_BACKUP.format(day=day)
            changes = (options["changes_out"]
                       or DEFAULT_CHANGES.format(day=day))
            filler = Filler(
                options["dry_run"], options["limit"], backup,
                verdicts=options["verdicts"], changes=changes)
            for line in filler.run():
                self.stdout.write(line)
