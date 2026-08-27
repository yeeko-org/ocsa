from space_time.management.commands._inegi_base import (
    CsvLoader, LoaderCommand, integer_or_none)
from space_time.models import Locality, Municipality

CSV_PATH = "space_time/geo_files/localidades.csv"
BATCH_SIZE = 10000
# `bulk_update` arma un CASE por lote: con lotes grandes el plan de
# Postgres se degrada (10,000 filas tardan más que 10 lotes de 1,000).
UPDATE_BATCH_SIZE = 1000
# La localidad 0001 de cada municipio es su cabecera
CABECERA_CODE = "0001"
RURAL_AMBITO = "R"
UPDATED_FIELDS = [
    "name", "population", "latitude", "longitude", "altitude",
    "is_rural", "is_current"]


class LoadLocalidades(CsvLoader):
    """Upsert por clave completa contra el corte vigente del AGEEML.

    Las localidades que el corte ya no trae se marcan `is_current=False`
    en vez de borrarse: hay ubicaciones capturadas que apuntan a ellas.
    """

    csv_path = CSV_PATH
    row_label = "la localidad"
    row_key = "CVE_LOC"

    def __init__(self, dry_run: bool = False):
        super().__init__(dry_run)
        self.municipalities = {
            row[0]: row
            for row in Municipality.objects.values_list(
                "complete_code", "id", "latitude", "longitude",
                "altitude")}
        self.existing = {
            row[1]: row
            for row in Locality.objects.values_list(
                "id", "complete_code", *UPDATED_FIELDS)}
        self.seen_codes: set[str] = set()
        self.pending: list[Locality] = []
        self.changed: list[Locality] = []
        self.cabeceras: list[Municipality] = []
        self.load_csv()
        self.flush()
        self.flush_changed()
        self.save_cabeceras()
        self.retired = self.retire()

    def read_row(self, row: dict) -> None:
        municipality_code = f"{row['CVE_ENT']}-{row['CVE_MUN']}"
        municipality = self.municipalities.get(municipality_code)
        municipality_id = municipality[1] if municipality else None
        inegi_code = row["CVE_LOC"]
        complete_code = f"{municipality_code}-{inegi_code}"
        self.seen_codes.add(complete_code)
        values = {
            "name": row["NOM_LOC"],
            "population": integer_or_none(row["POB_TOTAL"]),
            "latitude": float(row["LAT_DECIMAL"]),
            "longitude": float(row["LON_DECIMAL"]),
            # Dos docenas de localidades del corte traen la altitud vacía.
            "altitude": integer_or_none(row["ALTITUD"]),
            "is_rural": row["AMBITO"] == RURAL_AMBITO,
            "is_current": True,
        }
        if inegi_code == CABECERA_CODE and municipality:
            self.mark_cabecera(municipality, values)
        current = self.existing.get(complete_code)
        if current is None:
            self.create(complete_code, inegi_code, municipality_id, values)
            return
        row_id, _, *stored = current
        if [values[name] for name in UPDATED_FIELDS] == stored:
            return
        self.updated += 1
        self.changed.append(Locality(id=row_id, **values))
        if len(self.changed) >= BATCH_SIZE:
            self.flush_changed()

    def create(self, complete_code: str, inegi_code: str,
               municipality_id: int | None, values: dict) -> None:
        self.created += 1
        self.pending.append(Locality(
            inegi_code=inegi_code, complete_code=complete_code,
            municipality_id=municipality_id, **values))
        if len(self.pending) >= BATCH_SIZE:
            self.flush()

    def mark_cabecera(self, municipality: tuple, values: dict) -> None:
        coordinates = (
            values["latitude"], values["longitude"], values["altitude"])
        if municipality[2:] == coordinates:
            return
        self.cabeceras.append(Municipality(
            id=municipality[1], latitude=coordinates[0],
            longitude=coordinates[1], altitude=coordinates[2]))

    def flush(self) -> None:
        if not self.dry_run and self.pending:
            Locality.objects.bulk_create(self.pending)
        self.pending = []

    def flush_changed(self) -> None:
        if not self.dry_run and self.changed:
            Locality.objects.bulk_update(
                self.changed, UPDATED_FIELDS, batch_size=UPDATE_BATCH_SIZE)
        self.changed = []

    def save_cabeceras(self) -> None:
        if self.dry_run or not self.cabeceras:
            return
        Municipality.objects.bulk_update(
            self.cabeceras, ["latitude", "longitude", "altitude"],
            batch_size=500)

    def retire(self) -> int:
        """Marca como no vigentes las que el corte ya no trae."""
        stale = [
            row[0] for code, row in self.existing.items()
            if code not in self.seen_codes and row[-1]]
        if not self.dry_run and stale:
            Locality.objects.filter(id__in=stale).update(is_current=False)
        return len(stale)

    def report_counts(self) -> list[str]:
        return [
            f"{self.prefix}Localidades creadas: {self.created}",
            f"{self.prefix}Localidades actualizadas: {self.updated}",
            f"{self.prefix}Localidades retiradas del catálogo: {self.retired}",
            f"{self.prefix}Cabeceras actualizadas: {len(self.cabeceras)}",
            f"Total en la base: {Locality.objects.count()}",
        ]


class Command(LoaderCommand):
    help = "Sincroniza el catálogo de localidades del AGEEML con la base"
    loader_class = LoadLocalidades
    dry_run_help = "Solo reporta altas, cambios y retiros, sin escribir"
