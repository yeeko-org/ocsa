import csv

from django.core.management.base import BaseCommand

from actor.migrate.common import text_normalizer
from space_time.models import Municipality

CSV_PATH = "space_time/geo_files/municipios.csv"


class Command(BaseCommand):
    help = "Carga o actualiza el catálogo de municipios del AGEEML"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Solo reporta cuántos crearía y actualizaría")

    def handle(self, *args, **options):
        loader = LoadMunicipios(dry_run=options["dry_run"])
        for line in loader.report():
            self.stdout.write(line)


class LoadMunicipios:
    """Upsert por `complete_code` sobre el corte vigente del AGEEML.

    Idempotente a propósito: el catálogo se refresca con cortes
    irregulares (2024 agregó Juan José Ríos y Villa de Pozos) y el
    comando se vuelve a correr sobre una base que ya tiene datos.
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.created = 0
        self.updated = 0
        self.errors: list[str] = []
        self.states_ids = self.load_states()
        self.existing = {
            municipality.complete_code: municipality
            for municipality in Municipality.objects.all()}
        self.load_csv(CSV_PATH)

    @staticmethod
    def load_states() -> dict[str, int]:
        from space_time.models import State
        return {state.inegi_code: state.pk for state in State.objects.all()}

    def load_csv(self, file_path: str) -> None:
        with open(file_path, newline="", encoding="latin1") as csvfile:
            for row in csv.DictReader(csvfile):
                try:
                    self.upsert(row)
                except Exception as error:
                    self.errors.append(
                        f"Error en el municipio {row.get('CVE_MUN')}: {error}")

    def upsert(self, row: dict) -> None:
        inegi_code = row["CVE_MUN"]
        state_inegi_code = row["CVE_ENT"]
        complete_code = f"{state_inegi_code}-{inegi_code}"
        population = row["POB_TOTAL"] or ""
        values = {
            "inegi_code": inegi_code,
            "name": row["NOM_MUN"],
            "std_name": text_normalizer(row["NOM_MUN"]),
            "state_id": self.states_ids.get(state_inegi_code),
            "population": int(population) if population.isdigit() else None,
        }
        municipality = self.existing.get(complete_code)
        if municipality is None:
            self.created += 1
            if not self.dry_run:
                Municipality.objects.create(
                    complete_code=complete_code, **values)
            return
        changed = [
            field for field, value in values.items()
            if getattr(municipality, field) != value]
        if not changed:
            return
        self.updated += 1
        if self.dry_run:
            return
        for field in changed:
            setattr(municipality, field, values[field])
        municipality.save(update_fields=changed)

    def report(self) -> list[str]:
        prefix = "[dry-run] " if self.dry_run else ""
        lines = [
            f"{prefix}Municipios creados: {self.created}",
            f"{prefix}Municipios actualizados: {self.updated}",
            f"Total en la base: {Municipality.objects.count()}",
        ]
        lines.extend(self.errors)
        return lines
