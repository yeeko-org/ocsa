import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from actor.models import Actor
from classify.dated_comment import add_comment
from classify.models import IndigenousGroup
from utils.alternative_names import add_alternative_names, split_names
from work_flux.models import StatusControl


DEFAULT_PATH = (
    Path(__file__).resolve().parents[2] / "data"
    / "inpi_pueblos_2025-02-21.json")

# Decisiones de Ricardo del 2026-11-09, sobre el informe
# api/.claude/diagnostics/indigenous_merge_report.py. Entrada absorbida →
# denominación del DOF del pueblo destino. La dirección sigue la regla de
# nombres: queda la entrada que load_inpi_catalog adoptó (la homónima del
# nombre, de la autodenominación elegida o de la denominación del DOF) y
# las demás se fusionan hacia ella. Las cinco entradas compuestas («Mixe;
# Zapoteca; iKoot»…) y «Yumana» no se tocan.
MERGES = [
    ("Mixe", "Mixe"),
    ("Zapoteca", "Zapoteco"),
    ("Guarijíos", "Guarijío"),
    ("Macurawe", "Guarijío"),
    ("Huichol", "Huichol"),
    ("Ikoot", "Huave"),
    ("Mayo", "Mayo"),
    ("Mayo-yoreme", "Mayo"),
    ("Yoremes", "Mayo"),
    ("Náyeri", "Cora"),
    ("Purépecha", "Tarasco"),
    ("Tarahumaras", "Tarahumara"),
    ("Seris", "Seri"),
    ("Tlapanecos", "Tlapaneco"),
    ("Totonaca", "Totonaco"),
    ("Tzeltal", "Tseltal"),
    ("Yokotán", "Chontal de Tabasco"),
    ("Ñomdaa", "Amuzgo"),
    ("ñhöñhö", "Otomí"),
    ("Nahum", "Nahua"),
    ("Chontal", "Chontal de Oaxaca"),
    ("Xk'eek'en", "Maya"),
]
# Absorbidas cuyo nombre no pasa a los alternativos del destino.
DROP_NAME = {"Xk'eek'en"}  # es un cenote de Dzitnup, no un nombre del pueblo
# Actores que no se mueven aunque su entrada se absorba.
RETAINED = {
    6374: "se dejó en «{old}» aunque la entrada se fusionó en «{new}»: la "
          "asamblea es maseual (nahua), tutunaku (totonaca) y mestiza, no "
          "guarijía",
}
# Notas para revisar, sobre actores que la fusión mueve.
ACTOR_NOTES = {
    4822: "estaba clasificado en el pueblo «Zapoteca» y pasó a «{new}» al "
          "fusionar con el catálogo del INPI. Revisar la ubicación de sus "
          "proyectos: están fuera de Oaxaca (Campeche y Chiapas)",
    4760: "estaba clasificado en el pueblo «Zapoteca» y pasó a «{new}» al "
          "fusionar con el catálogo del INPI. Revisar la ubicación de sus "
          "proyectos: además de Oaxaca, hay uno en Baja California",
    2851: "estaba clasificado en el pueblo «Tzeltal» y pasó a «{new}» al "
          "fusionar con el catálogo del INPI. Revisar: no necesariamente "
          "es tseltal",
    3859: "estaba clasificado en «Xk'eek'en», un cenote de Dzitnup "
          "registrado como pueblo, y pasó a «{new}» al fusionar con el "
          "catálogo del INPI",
}


class Command(BaseCommand):
    help = (
        "Fusiona entradas de IndigenousGroup en el pueblo oficial del INPI: "
        "mueve sus actores, pasa el nombre absorbido a los alternativos del "
        "oficial y borra la absorbida; si retiene actores, la marca "
        "could_reclassify con un comentario. Idempotente. Va después de "
        "load_inpi_catalog y tidy_indigenous_groups; el índice del mapa no "
        "incluye pueblos.")

    def add_arguments(self, parser):
        parser.add_argument("--path", default=str(DEFAULT_PATH))
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Corre todo dentro de una transacción y la revierte.")

    def handle(self, *args, **opts):
        path = Path(opts["path"])
        if not path.exists():
            raise CommandError(f"No existe {path}")
        pueblos = json.loads(path.read_text(encoding="utf-8"))["pueblos"]
        names = {p["dof_name"]: p["name"] for p in pueblos}
        retain_status = StatusControl.objects.filter(
            group_id="validation", name="could_reclassify").first()
        if not retain_status:
            raise CommandError(
                "Falta el StatusControl de validación could_reclassify")

        with transaction.atomic():
            lines, counts = self.merge_all(names, retain_status)
            if opts["dry_run"]:
                transaction.set_rollback(True)

        for line in lines:
            self.stdout.write(line)
        prefix = "[dry-run, revertido] " if opts["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}{counts['merged']} fusionadas ({counts['deleted']} "
            f"borradas), {counts['done']} ya estaban, {counts['missing']} "
            f"sin entrada o destino; "
            f"{counts['moved']} actores movidos, {counts['retained']} "
            f"retenidos, {counts['notes']} notas en actores"))

    def merge_all(self, names, retain_status):
        lines = []
        counts = dict.fromkeys(
            ["merged", "deleted", "done", "missing", "moved", "retained",
             "notes"], 0)
        for old, dof_name in MERGES:
            target_name = names.get(dof_name, dof_name)
            target = IndigenousGroup.objects.filter(
                is_official=True, name=target_name).first()
            source = next(
                (g for g in IndigenousGroup.objects.filter(
                    is_official=False).order_by("id")
                 if g.name.strip() == old), None)
            if not target or not source:
                counts["missing"] += 1
                # Una absorbida sin actores se borra al fusionarla: en la
                # segunda corrida ya no existe.
                why = ("no existe la entrada (¿ya fusionada y borrada?)"
                       if target else
                       "sin destino oficial (¿corrió load_inpi_catalog?)")
                lines.append(f"FALTA «{old}» → «{target_name}»: {why}")
                continue
            done = self.merge(source, target, retain_status, counts)
            lines.append(done)
        return lines, counts

    def merge(self, source, target, retain_status, counts) -> str:
        actors = list(Actor.objects.filter(
            indigenous_group=source).order_by("id"))
        moving = [a for a in actors if a.id not in RETAINED]
        retained = [a for a in actors if a.id in RETAINED]
        label = f"#{source.id} «{source.name.strip()}» → #{target.id} " \
                f"«{target.name}»"
        # Sin ids en el comentario (decisión de Ricardo): la marca es el
        # nombre del destino, y los ids para deshacer van solo en la salida.
        merged_mark = f"fusionada en «{target.name}»"
        already = (source.status_validation_id == retain_status.pk
                   and merged_mark in (source.comments or ""))
        if already and retained and not moving:
            counts["done"] += 1
            return f"YA FUSIONADA {label}"

        for actor in moving:
            actor.indigenous_group = target
            update = ["indigenous_group"]
            note = ACTOR_NOTES.get(actor.id)
            if note and add_comment(actor, note.format(new=target.name)):
                update.append("comments")
                counts["notes"] += 1
            actor.save(update_fields=update)
        for actor in retained:
            text = RETAINED[actor.id].format(
                old=source.name.strip(), new=target.name)
            if add_comment(actor, text):
                actor.save(update_fields=["comments"])
                counts["notes"] += 1

        kept_name = source.name.strip() not in DROP_NAME
        if kept_name:
            names = [source.name.strip()]
            names += split_names(source.alternative_names)
            if add_alternative_names(target, names):
                target.save(update_fields=["alternative_names"])

        ids = ", ".join(str(a.id) for a in moving) or "-"
        counts["merged"] += 1
        counts["moved"] += len(moving)
        counts["retained"] += len(retained)
        if not retained:
            # Su nombre ya vive en los alternativos del destino y los ids
            # para deshacer quedan en la salida (task-140).
            source.delete()
            counts["deleted"] += 1
            line = (f"FUSIONADA Y BORRADA {label}: {len(moving)} actores "
                    f"movidos ({ids})")
            if not kept_name:
                line += ", sin conservar el nombre"
            return line

        # Si retiene actores, la entrada sigue en uso: could_reclassify deja
        # abierta su clasificación.
        text = f"{merged_mark}; se movieron {len(moving)} actores"
        if len(retained) == 1:
            text += "; se retuvo 1 actor"
        else:
            text += f"; se retuvieron {len(retained)} actores"
        add_comment(source, text)
        source.status_validation = retain_status
        source.save(update_fields=["status_validation", "comments"])
        line = f"FUSIONADA {label}: {len(moving)} actores movidos ({ids})"
        line += "; retenidos en la absorbida: " + ", ".join(
            str(a.id) for a in retained)
        if not kept_name:
            line += ", sin conservar el nombre"
        return line
