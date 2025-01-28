from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from impact.models import Impact
from ocsa_legacy.models import RegistroNotas
from source.models import Note


AE_TO_TYPE_IMPACT = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 7,
}

CAPTURE_DATE_MATCH = "2025-01-21"


class Command(BaseCommand):
    help = "Recovery fecha_captura and descripcion_ae from legacy data"

    def handle(self, *args, **kwargs):
        total = RegistroNotas.objects.count()
        not_found = 0
        for registro in RegistroNotas.objects.all():

            datum = registro.datum
            if not datum:
                continue

            title = datum.get("nota", {}).get("titulo")
            if not title:
                continue
            notes_query = Note.objects.filter(title=title)
            notes_count = notes_query.count()
            if notes_count == 0:
                self.stdout.write(
                    self.style.ERROR(f"Not found: Note with title {title}"))

                not_found += 1
                continue
            if notes_count > 1:
                self.stdout.write(
                    self.style.WARNING(
                        f"Multiple notes({notes_count}) with title {title}"))

            fecha_captura = datum.get("nota", {}).get("fecha_captura")
            afectacion_ecologica = datum.get("afectacionEcologica", [])

            ae_data = {}

            for ae in afectacion_ecologica:  # type: ignore
                tipo_ae_id = ae.get("tipo_ae_id")
                if tipo_ae_id not in AE_TO_TYPE_IMPACT:
                    continue

                descripcion_ae = ae.get("descripcion_ae")
                if not tipo_ae_id:
                    continue
                if not tipo_ae_id in ae_data:
                    ae_data[tipo_ae_id] = []

                ae_data[tipo_ae_id].append(descripcion_ae)

            self.update_note_data(title, fecha_captura, ae_data)

        self.stdout.write(
            self.style.SUCCESS(f"Total: {total}, Not found: {not_found}"))

    def update_note_data(self, note_title: str, fecha_captura: str, ae_data: dict):

        parsed_date = parse_datetime(fecha_captura)
        new_capture_date = parsed_date.date() if parsed_date else None
        if new_capture_date:
            Note.objects.filter(capture_date=CAPTURE_DATE_MATCH)\
                .update(capture_date=new_capture_date)

        if not ae_data:
            return
        for tipo_ae_id, descriptions in ae_data.items():
            if len(descriptions) != 1:
                continue

            query = Impact.objects\
                .filter(
                    mention__note__title=note_title,
                    impact_type__id=AE_TO_TYPE_IMPACT[tipo_ae_id],
                    description__isnull=True
                )
            self.stdout.write(self.style.SUCCESS(
                f"{note_title} Impact Total: {query.count()}, descriptions: {descriptions}"))

            results = query.update(description=descriptions[0])

            self.stdout.write(self.style.SUCCESS(
                f"{note_title} Impact Updated: {results}"))
