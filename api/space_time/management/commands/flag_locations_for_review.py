"""Marca para revisión editorial las ubicaciones que no cuadran.

Solo lee argumentos: la selección, la escritura y la reversa viven en
`space_time/review_flags.py`, porque también las usan los tests.

Uso:
    python manage.py flag_locations_for_review              # solo reporta
    python manage.py flag_locations_for_review --apply
    python manage.py flag_locations_for_review --locality-threshold 5
    python manage.py flag_locations_for_review --apply --expect 60
    python manage.py flag_locations_for_review --revert <csv>
"""

from datetime import date

from django.core.management.base import BaseCommand

from space_time.far_pins import LOCALITY_THRESHOLD_KM, THRESHOLD_KM
from space_time.review_flags import DEFAULT_OUT, Flagger, Reverter


class Command(BaseCommand):
    help = ("Agrega comentario fechado —y pasa de «Aprobado» a «Aprobado "
            "(con observaciones)»— a las ubicaciones con pin lejos del "
            "municipio o de la localidad capturados, trazo fuera del "
            "municipio capturado o lejos de la localidad capturada, estado "
            "que no es el del municipio, o localidad del legado "
            "irresoluble.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Escribe los cambios. Sin esta bandera solo reporta.")
        parser.add_argument(
            "--out", default="",
            help="CSV de lo que cambiaría (default: "
                 + DEFAULT_OUT.format(day="<fecha>") + ")")
        parser.add_argument(
            "--threshold", type=float, default=THRESHOLD_KM,
            help=f"Kilómetros al municipio capturado a partir de los "
                 f"cuales el pin se marca (default: {THRESHOLD_KM})")
        parser.add_argument(
            "--locality-threshold", type=float, default=LOCALITY_THRESHOLD_KM,
            help=f"Kilómetros a la localidad capturada a partir de los "
                 f"cuales se marcan el pin y el trazo; no lo hereda de "
                 f"--threshold (default: {LOCALITY_THRESHOLD_KM})")
        parser.add_argument(
            "--expect", type=int, default=None,
            help="Cuenta esperada; aborta si la selección se desvía más "
                 "del 5 %%.")
        parser.add_argument(
            "--revert", default="",
            help="Deshace una corrida desde el CSV que dejó: restaura el "
                 "estatus previo y quita el comentario agregado.")

    def handle(self, *args, **options):
        if options["revert"]:
            for line in Reverter(options["revert"]).run():
                self.stdout.write(line)
            return
        day = date.today().isoformat()
        out = options["out"] or DEFAULT_OUT.format(day=day)
        flagger = Flagger(
            options["apply"], out, threshold=options["threshold"],
            expect=options["expect"],
            locality_threshold=options["locality_threshold"])
        for line in flagger.run():
            self.stdout.write(line)
