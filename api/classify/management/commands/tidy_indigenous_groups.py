from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from actor.models import Actor
from classify.models import IndigenousGroup
from work_flux.models import StatusControl


# Decisiones de Ricardo del 2026-11-08, previas a cargar el catálogo del
# INPI. Las cinco entradas compuestas («Mixe; Zapoteca; iKoot»…) no se tocan:
# esperan la migración de indigenous_group a muchos a muchos.
COMMENT_PREFIX = "08/11/2026 - Ricardo: "
# «Comunidades aledañas» se decidió un día después, igual que Ciudadanos.
LATER_PREFIX = "09/11/2026 - Ricardo: "
NAHUA_NOTE = (
    "son nahuas históricos; si se fusiona en Nahua, agregar este nombre a "
    "nombres alternativos")
RENAMES = [
    # (nombre actual, nombre nuevo, status)
    ("NE", "Pueblo no especificado", "need_reclassify"),
]
NOT_PEOPLES = [
    ("Ciudadanos", COMMENT_PREFIX),
    ("Vecinos", COMMENT_PREFIX),
    ("Comunidades aledañas", LATER_PREFIX),
]
TO_RECLASSIFY = [
    ("Acolhuas", NAHUA_NOTE),
    ("Cholulteco", NAHUA_NOTE),
    ("Comunidad indigena de Ixcotla",
     "es una comunidad de Molango, Hidalgo, no un pueblo; averiguar el "
     "pueblo"),
]


def add_comment(group, text, prefix=COMMENT_PREFIX) -> bool:
    comment = f"{prefix}{text}"
    if comment in (group.comments or ""):
        return False
    group.comments = (
        f"{group.comments}\n\n{comment}" if group.comments else comment)
    return True


class Command(BaseCommand):
    help = (
        "Limpia entradas de IndigenousGroup que no son pueblos: renombra NE, "
        "vacía Ciudadanos, Vecinos y Comunidades aledañas, y marca para "
        "reclasificar las que son nombres históricos o lugares. "
        "Idempotente.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Corre todo dentro de una transacción y la revierte.")

    def handle(self, *args, **opts):
        statuses = {
            s.name: s
            for s in StatusControl.objects.filter(group_id="validation")}
        needed = {"need_reclassify", "expired", "could_reclassify"}
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

        for name, prefix in NOT_PEOPLES:
            group = self.get(name)
            if not group:
                lines.append(f"NO EXISTE «{name}»")
                continue
            actor_ids = list(
                Actor.objects.filter(indigenous_group=group)
                .order_by("id").values_list("id", flat=True))
            if actor_ids:
                Actor.objects.filter(id__in=actor_ids).update(
                    indigenous_group=None)
                # Sin ids en el comentario (decisión de Ricardo): para
                # deshacerlo, la salida de la corrida los lista.
                add_comment(group, (
                    f"no es un pueblo; se quitó de {len(actor_ids)} "
                    "actores"), prefix)
            group.status_validation = statuses["expired"]
            group.save()
            lines.append(
                f"CADUCO #{group.id} «{name}»: {len(actor_ids)} actores "
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
