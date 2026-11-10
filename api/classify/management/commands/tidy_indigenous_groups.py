from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from actor.models import Actor
from classify.dated_comment import add_comment
from classify.models import IndigenousGroup
from work_flux.models import StatusControl


# Decisiones de Ricardo del 2026-11-08, previas a cargar el catálogo del
# INPI. Las cinco entradas compuestas («Mixe; Zapoteca; iKoot»…) no se tocan:
# esperan la migración de indigenous_group a muchos a muchos.
NAHUA_NOTE = (
    "son nahuas históricos; si se fusiona en Nahua, agregar este nombre a "
    "nombres alternativos")
RENAMES = [
    # (nombre actual, nombre nuevo, status)
    ("NE", "Pueblo no especificado", "need_reclassify"),
]
# No son pueblos: se quitan de sus actores y se borran (task-140); los ids
# para deshacerlo quedan solo en la salida de la corrida.
NOT_PEOPLES = ["Ciudadanos", "Vecinos", "Comunidades aledañas"]
TO_RECLASSIFY = [
    ("Acolhuas", NAHUA_NOTE),
    ("Cholulteco", NAHUA_NOTE),
    ("Comunidad indigena de Ixcotla",
     "es una comunidad de Molango, Hidalgo, no un pueblo; averiguar el "
     "pueblo"),
]


class Command(BaseCommand):
    help = (
        "Limpia entradas de IndigenousGroup que no son pueblos: renombra NE, "
        "quita Ciudadanos, Vecinos y Comunidades aledañas de sus actores y "
        "las borra, y marca para reclasificar las que son nombres "
        "históricos o lugares. Idempotente.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Corre todo dentro de una transacción y la revierte.")

    def handle(self, *args, **opts):
        statuses = {
            s.name: s
            for s in StatusControl.objects.filter(group_id="validation")}
        needed = {"need_reclassify", "could_reclassify"}
        if missing := needed - set(statuses):
            raise CommandError(f"Faltan status de validación: {missing}")

        with transaction.atomic():
            lines = self.tidy(statuses)
            if opts["dry_run"]:
                transaction.set_rollback(True)

        for line in lines:
            self.stdout.write(line)
        prefix = "[dry-run, revertido] " if opts["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(f"{prefix}listo"))

    def tidy(self, statuses) -> list[str]:
        lines = []
        for old, new, status in RENAMES:
            group = self.get(old) or self.get(new)
            if not group:
                lines.append(f"NO EXISTE «{old}»")
                continue
            lines.append(
                f"RENOMBRADO #{group.id} «{group.name}» → «{new}» "
                f"({status})")
            group.name = new
            group.status_validation = statuses[status]
            group.save()

        for name in NOT_PEOPLES:
            group = self.get(name)
            if not group:
                lines.append(f"NO EXISTE «{name}» (¿ya borrada?)")
                continue
            actor_ids = list(
                Actor.objects.filter(indigenous_group=group)
                .order_by("id").values_list("id", flat=True))
            # El FK de Actor es CASCADE: sin vaciarlo, borrar la entrada
            # borraría sus actores.
            Actor.objects.filter(id__in=actor_ids).update(
                indigenous_group=None)
            group_id = group.id
            group.delete()
            lines.append(
                f"BORRADA #{group_id} «{name}»: {len(actor_ids)} actores "
                f"pasados a null ({', '.join(map(str, actor_ids)) or '-'})")

        for name, note in TO_RECLASSIFY:
            group = self.get(name)
            if not group:
                lines.append(f"NO EXISTE «{name}»")
                continue
            group.status_validation = statuses["could_reclassify"]
            commented = add_comment(group, note)
            group.save()
            lines.append(
                f"POR RECLASIFICAR #{group.id} «{name}»"
                f"{' + comentario' if commented else ''}")
        return lines

    @staticmethod
    def get(name):
        # Hay nombres heredados con espacios de sobra («Guarijíos »).
        return next((g for g in IndigenousGroup.objects.order_by("id")
                     if g.name.strip() == name), None)
