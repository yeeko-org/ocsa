from actor.migrate.common import text_normalizer
from space_time.management.commands._inegi_base import (
    CsvLoader, LoaderCommand, integer_or_none)
from space_time.models import Municipality

CSV_PATH = "space_time/geo_files/municipios.csv"


class LoadMunicipios(CsvLoader):
    """Upsert por `complete_code` sobre el corte vigente del AGEEML.

    Idempotente a propósito: el catálogo se refresca con cortes irregulares
    y el comando se vuelve a correr sobre una base que ya tiene datos.
    """

    csv_path = CSV_PATH
    row_label = "el municipio"
    row_key = "CVE_MUN"

    def __init__(self, dry_run: bool = False):
        super().__init__(dry_run)
        self.states_ids = self.load_states()
        self.existing = {
            municipality.complete_code: municipality
            for municipality in Municipality.objects.all()}
        self.load_csv()

    @staticmethod
    def load_states() -> dict[str, int]:
        from space_time.models import State
        return {state.inegi_code: state.pk for state in State.objects.all()}

    def read_row(self, row: dict) -> None:
        inegi_code = row["CVE_MUN"]
        state_inegi_code = row["CVE_ENT"]
        complete_code = f"{state_inegi_code}-{inegi_code}"
        values = {
            "inegi_code": inegi_code,
            "name": row["NOM_MUN"],
            "std_name": text_normalizer(row["NOM_MUN"]),
            "state_id": self.states_ids.get(state_inegi_code),
            "population": integer_or_none(row["POB_TOTAL"]),
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

    def report_counts(self) -> list[str]:
        return [
            f"{self.prefix}Municipios creados: {self.created}",
            f"{self.prefix}Municipios actualizados: {self.updated}",
            f"Total en la base: {Municipality.objects.count()}",
        ]


class Command(LoaderCommand):
    help = "Carga o actualiza el catálogo de municipios del AGEEML"
    loader_class = LoadMunicipios
    dry_run_help = "Solo reporta cuántos crearía y actualizaría"
