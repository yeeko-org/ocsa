"""Diagnostica huecos en los lotes de scraping ya registrados.

Solo lectura. Responde tres cosas antes de decidir una recuperación
histórica:

  - Qué secciones el scraper vio pero de las que nunca extrajo artículos
    (bug de selector, no de red).
  - Qué días quedaron con secciones caídas por error de acceso.
  - Qué días simplemente no tuvieron edición (festivos), para no
    confundirlos con fallos.

    python manage.py diagnose_scraping_gaps
    python manage.py diagnose_scraping_gaps --source "La Jornada"

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registradas.
"""

from collections import Counter, defaultdict

from django.core.management.base import BaseCommand

from source.models import Article, ScrapedRecord, Source


class Command(BaseCommand):
    help = "Reporta secciones vacías, días caídos y festivos en los lotes."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--source", type=str, default=None,
            help="Nombre de la fuente a diagnosticar (default: todas).")

    def handle(self, *args, **options) -> None:
        sources = Source.objects.all()
        if options["source"]:
            sources = sources.filter(name__icontains=options["source"])
            if not sources.exists():
                self.stderr.write(f"Sin fuentes que coincidan.")
                return

        self._report_scope(sources)
        for source in sources:
            self._report_source(source)

    def _header(self, text: str) -> None:
        self.stdout.write(f"\n{'=' * 70}")
        self.stdout.write(self.style.MIGRATE_HEADING(text))
        self.stdout.write("=" * 70)

    def _report_scope(self, sources) -> None:
        self._header("ALCANCE")
        for source in sources:
            records = ScrapedRecord.objects.filter(source=source)
            if not records.exists():
                continue
            first = records.order_by("from_date").first()
            last = records.order_by("-from_date").first()
            articles = Article.objects.filter(source=source).count()
            self.stdout.write(
                f"  {source.name:15} {records.count():4} lotes  "
                f"{first.from_date} → {last.to_date}  {articles:6} artículos")

    def _classify_days(self, source: Source) -> dict:
        """
        Reparte los días de todos los lotes en categorías excluyentes.

        Un día sin `articles` ni `url` en su payload no es un fallo del
        scraper: es una fecha sin edición (festivo), donde la URL del día
        no existe y se guardó el error de acceso en lugar de secciones.
        """
        result = {
            "normal": [], "holiday": [], "empty": [],
            "with_errors": [], "records_no_data": [],
        }
        section_names = Counter()
        empty_sections = Counter()
        filled_sections = defaultdict(list)
        error_sections = Counter()

        records = ScrapedRecord.objects.filter(source=source)
        for record in records:
            if not record.data:
                result["records_no_data"].append(
                    (record.id, record.from_date, record.to_date))
                continue
            for date_, sections in record.data.items():
                if not isinstance(sections, dict):
                    continue
                payloads = [
                    s for s in sections.values() if isinstance(s, dict)]
                if not any("url" in s or "articles" in s for s in payloads):
                    result["holiday"].append((date_, record.id))
                    continue

                total = 0
                has_error = False
                for name, payload in sections.items():
                    if not isinstance(payload, dict):
                        continue
                    section_names[name] += 1
                    if payload.get("error"):
                        error_sections[name] += 1
                        has_error = True
                        continue
                    count = len(payload.get("articles") or [])
                    total += count
                    if count:
                        filled_sections[name].append(count)
                    else:
                        empty_sections[name] += 1

                if has_error:
                    result["with_errors"].append((date_, record.id))
                elif total == 0:
                    result["empty"].append((date_, record.id))
                else:
                    result["normal"].append((date_, record.id))

        result["section_names"] = section_names
        result["empty_sections"] = empty_sections
        result["filled_sections"] = filled_sections
        result["error_sections"] = error_sections
        return result

    def _report_source(self, source: Source) -> None:
        data = self._classify_days(source)
        if not any(data[k] for k in
                   ("normal", "holiday", "empty", "with_errors")):
            return

        self._header(f"{source.name} — días por categoría")
        self.stdout.write(f"  con artículos:        {len(data['normal']):5}")
        self.stdout.write(f"  sin edición (festivo):{len(data['holiday']):5}")
        self.stdout.write(f"  vacíos (0 artículos): {len(data['empty']):5}")
        self.stdout.write(f"  con secciones caídas: {len(data['with_errors']):5}")
        for date_, record_id in sorted(data["holiday"]):
            self.stdout.write(f"      festivo {date_} (lote {record_id})")
        for date_, record_id in sorted(data["empty"]):
            self.stdout.write(f"      vacío   {date_} (lote {record_id})")

        if data["records_no_data"]:
            self.stdout.write(self.style.WARNING(
                f"\n  Lotes sin `data` (fallaron antes de guardar nada): "
                f"{len(data['records_no_data'])}"))
            for record_id, from_date, to_date in data["records_no_data"]:
                self.stdout.write(
                    f"      lote {record_id}: {from_date} → {to_date}")

        self._report_sections(data)
        self._report_errors(data)

    def _report_sections(self, data: dict) -> None:
        """Secciones que el scraper vio pero de las que nunca extrajo nada."""
        never_filled = {
            name: count for name, count in data["section_names"].items()
            if name not in data["filled_sections"]
        }
        self.stdout.write("\n  Secciones vistas y su rendimiento:")
        for name, seen in data["section_names"].most_common():
            filled = data["filled_sections"].get(name) or []
            if not filled:
                self.stdout.write(self.style.ERROR(
                    f"      {name:24} vista {seen:5} veces, "
                    f"SIEMPRE 0 artículos  <-- bug de selector"))
                continue
            avg = sum(filled) / len(filled)
            empty = data["empty_sections"].get(name, 0)
            note = f"  ({empty} días en 0)" if empty else ""
            self.stdout.write(
                f"      {name:24} vista {seen:5} veces, "
                f"~{avg:5.1f} art/día{note}")

        if never_filled:
            total = sum(never_filled.values())
            self.stdout.write(self.style.WARNING(
                f"\n  Universo de recuperación: {total} días-sección "
                f"en {len(never_filled)} secciones."))

    def _report_errors(self, data: dict) -> None:
        if not data["error_sections"]:
            self.stdout.write(self.style.SUCCESS(
                "\n  Sin secciones caídas por error de acceso."))
            return
        self.stdout.write("\n  Secciones caídas y pérdida estimada:")
        total_lost = 0
        for name, days in data["error_sections"].most_common():
            filled = data["filled_sections"].get(name) or []
            avg = sum(filled) / len(filled) if filled else 0
            lost = int(round(avg * days))
            total_lost += lost
            self.stdout.write(
                f"      {name:24} {days:4} días  ~{avg:5.1f} art/día  "
                f"→ ~{lost} perdidos")
        self.stdout.write(self.style.WARNING(
            f"      PÉRDIDA ESTIMADA: ~{total_lost} artículos"))
