"""Borra las ubicaciones huérfanas cuyo padre legacy no existe en el
modelo nuevo.

En el legacy una `ubicacion` colgaba de siete rutas distintas (seis tablas
puente más el FK suelto de `poblaciones_afectadas`). El modelo nuevo solo
admite tres padres —proyecto, evento e impacto—, así que las ubicaciones
que colgaban de un **opositor** o de una **población afectada** se
migraron sin destino posible, igual que las que ya no colgaban de nada.
Esas son las que este comando borra; las que perdieron un enlace que sí
tenía destino (proyecto, violencia, acción colectiva, afectación) se
respetan, porque ahí el vínculo es recuperable.

No deja archivo de respaldo a propósito: el schema `ocs` **es** el
respaldo. Cada fila borrada se puede reconstruir desde
`ocs.ubicaciones` por su `ubicacion_id_ref`, y su vínculo original desde
`ocs.opositores_to_ubicaciones` o `ocs.poblaciones_afectadas`.

Uso:
    python manage.py purge_orphan_locations              # solo reporta
    python manage.py purge_orphan_locations --apply
    python manage.py purge_orphan_locations --apply --expect 3103
    python manage.py purge_orphan_locations --dashboard-orphans
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.models import Count
from django.db.utils import ConnectionDoesNotExist

from space_time.models import Location

# Rutas legacy con destino en el modelo nuevo: si la ubicación aparece en
# alguna de ellas, su enlace se perdió y es recuperable, así que no se
# borra.
LINKED_ROUTES = (
    ("proyecto", "ProyectoToUbicacion"),
    ("violencia", "ViolenciaToUbicacion"),
    ("accion_colectiva", "AccionColectivaToUbicacion"),
    ("afectacion_ecologica", "AfectacionEcologicaToUbicacion"),
    ("afectacion_social", "AfectacionSocialToUbicacion"),
)

# Rutas legacy sin destino posible en el modelo nuevo.
ORPHAN_ROUTES = (
    ("opositor", "OpositorToUbicaciones"),
    ("poblacion_afectada", "PoblacionAfectada"),
)


class Command(BaseCommand):
    help = ("Borra las ubicaciones sin padre cuya ruta legacy era un "
            "opositor, una población afectada o ninguna.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="Ejecuta el borrado. Sin esta bandera solo reporta.")
        parser.add_argument(
            "--dashboard-orphans", action="store_true",
            help="Agrega las ubicaciones sin referencia legacy que nacieron "
                 "sin padre en el dashboard y no aportan nada: sin dato, "
                 "equivalentes a una hermana con padre, o copias dentro de "
                 "su propio grupo de duplicados.")
        parser.add_argument(
            "--expect", type=int, default=None,
            help="Cuenta esperada; aborta si la selección se desvía más "
                 "del 5 %%.")

    def handle(self, *args, **options):
        self.check_legacy_connection()
        selected, classes = self.select()
        if options["dashboard_orphans"]:
            selected, classes = self.add_dashboard_orphans(selected, classes)
        self.report(selected, classes)
        self.check_guards(selected)
        self.check_expected(selected.count(), options["expect"])

        if not options["apply"]:
            self.stdout.write(self.style.WARNING(
                "\nSimulación: no se borró nada. Repite con --apply."))
            return

        total = selected.count()
        # `delete()` de queryset no dispara `Location.delete`, que solo
        # tenía sentido para recalcular el estatus del proyecto padre —
        # y aquí ninguna fila tiene proyecto.
        deleted, _ = selected.delete()
        self.stdout.write(self.style.SUCCESS(
            f"\nBorradas {total} ubicaciones ({deleted} filas en total, "
            f"incluidas relaciones en cascada)."))

    def check_legacy_connection(self):
        """Sin la base legacy la selección no es computable: el criterio
        vive en las tablas puente del schema `ocs`."""
        try:
            connections["legacy"].ensure_connection()
        except ConnectionDoesNotExist:
            raise CommandError(
                "No hay conexión 'legacy' configurada: define las "
                "variables DATABASE_LEGACY_* (y DATABASE_LEGACY_SCHEMA=ocs) "
                "en el .env antes de correr esto.")
        except Exception as error:
            raise CommandError(f"La base legacy no responde: {error}")

    def route_ids(self, model_name):
        from ocsa_legacy import models as legacy
        model = getattr(legacy, model_name)
        return set(
            model.objects.exclude(ubicacion_id=None)
            .values_list("ubicacion_id", flat=True))

    def select(self):
        orphans = Location.objects.filter(
            project__isnull=True, event__isnull=True, impact__isnull=True,
            ubicacion_id_ref__isnull=False)
        refs = set(orphans.values_list("ubicacion_id_ref", flat=True))

        linked = set()
        for _, model_name in LINKED_ROUTES:
            linked |= self.route_ids(model_name)

        classes = {}
        purgeable = set()
        for label, model_name in ORPHAN_ROUTES:
            ids = (refs & self.route_ids(model_name)) - linked
            classes[label] = ids
            purgeable |= ids
        classes["sin_padre_legacy"] = refs - linked - purgeable
        purgeable |= classes["sin_padre_legacy"]
        classes["enlace_recuperable_no_se_borra"] = refs & linked

        selected = orphans.filter(ubicacion_id_ref__in=purgeable)
        return selected, classes

    @staticmethod
    def group_key(location):
        """Clave de deduplicación: `text_normalizer` deja solo letras y
        dígitos, así que «Col. Santa Cruz Atoyac» y «Santa Cruz Atoyac»
        quedan comparables por contención."""
        from actor.migrate.common import text_normalizer
        return (text_normalizer(location.details or "") or "",
                location.state_id, location.municipality_id)

    def add_dashboard_orphans(self, selected, classes):
        """Ubicaciones nacidas sin padre en el dashboard (sin referencia
        legacy) que no aportan información nueva.

        Se conserva la primera de cada grupo de duplicados —la de menor
        id— siempre que tenga texto, trazo o coordenadas y no exista ya una
        hermana con padre que diga lo mismo.
        """
        orphans = list(
            Location.objects.filter(
                project__isnull=True, event__isnull=True,
                impact__isnull=True, ubicacion_id_ref__isnull=True)
            .order_by("id"))

        # Hermanas con padre, indexadas por (estado, municipio): el
        # equivalente pide coincidencia de lugar, salvo que la huérfana no
        # tenga estado o municipio capturados —ahí el texto manda, porque
        # el lugar vacío no contradice a nadie (decisión de Ricardo,
        # 2026-08-28, caso «Puente Coahuayana»).
        siblings = {}
        anywhere = []
        for other in Location.objects.exclude(
                project__isnull=True, event__isnull=True,
                impact__isnull=True):
            key = self.group_key(other)
            siblings.setdefault((key[1], key[2]), []).append(key[0])
            anywhere.append(key[0])

        empty, twin, duplicated = set(), set(), set()
        seen = set()
        for location in orphans:
            normalized, state_id, municipality_id = self.group_key(location)
            # Estado y municipio solos no salvan a una fila: sin texto, sin
            # trazo y sin coordenadas no hay nada que revisar.
            has_data = bool(location.details or location.geojson
                            or location.latitude or location.longitude)
            candidates = (
                anywhere if not (state_id and municipality_id)
                else siblings.get((state_id, municipality_id), []))
            equivalent = normalized and any(
                other and (other == normalized or other in normalized
                           or normalized in other)
                for other in candidates)
            if not has_data:
                empty.add(location.id)
            elif equivalent:
                twin.add(location.id)
            elif (normalized, state_id, municipality_id) in seen:
                duplicated.add(location.id)
            seen.add((normalized, state_id, municipality_id))

        classes["dashboard_sin_dato"] = empty
        classes["dashboard_con_hermana_con_padre"] = twin
        classes["dashboard_copia_de_su_grupo"] = duplicated
        classes["dashboard_para_revisar_no_se_borra"] = {
            location.id for location in orphans
        } - empty - twin - duplicated

        ids = set(selected.values_list("id", flat=True))
        ids |= empty | twin | duplicated
        return Location.objects.filter(id__in=ids), classes

    def report(self, selected, classes):
        self.stdout.write(
            "Clases (las legacy se cuentan por ubicación del schema `ocs`; "
            "las de dashboard, por ubicación nueva):")
        for label, ids in classes.items():
            mark = "  " if label.endswith("no_se_borra") else "→ "
            self.stdout.write(f"  {mark}{label}: {len(ids)}")
        self.stdout.write(f"\nSeleccionadas para borrar: {selected.count()}")
        self.stdout.write("Por estatus:")
        for row in (selected.values("status_location_id")
                    .annotate(n=Count("id")).order_by("-n")):
            self.stdout.write(
                f"  {row['status_location_id']}: {row['n']}")
        sample = list(selected.order_by("id")
                      .values_list("id", "ubicacion_id_ref")[:5])
        self.stdout.write(f"Muestra (id, ubicacion_id_ref): {sample}")

    def check_guards(self, selected):
        """Ninguna fila a borrar debe tener contenido propio ni ser
        referida desde el sistema vivo."""
        from task.models import ClickHistory
        problems = []
        clicks = ClickHistory.objects.filter(location__in=selected).count()
        if clicks:
            problems.append(f"{clicks} registros de ClickHistory apuntan a "
                            f"ubicaciones seleccionadas")
        crossed = selected.filter(municipalities__isnull=False)\
            .distinct().count()
        if crossed:
            problems.append(f"{crossed} tienen municipios atravesados")
        with_geo = selected.filter(geojson__isnull=False).count()
        if with_geo:
            problems.append(f"{with_geo} tienen geojson")
        if problems:
            raise CommandError(
                "Salvaguardas incumplidas, no se borra nada:\n  - "
                + "\n  - ".join(problems))
        self.stdout.write(self.style.SUCCESS(
            "Salvaguardas: sin clics, sin municipios atravesados, "
            "sin geojson."))

    def check_expected(self, count, expected):
        if expected is None:
            return
        deviation = abs(count - expected) / expected if expected else 1
        if deviation > 0.05:
            raise CommandError(
                f"La selección ({count}) se desvía {deviation:.1%} de lo "
                f"esperado ({expected}); revisa antes de borrar.")
        self.stdout.write(
            f"Desviación contra --expect {expected}: {deviation:.1%}.")
