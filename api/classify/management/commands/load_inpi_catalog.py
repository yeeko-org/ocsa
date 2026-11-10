import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from classify.models import IndigenousGroup
from space_time.models import State
from utils.alternative_names import (
    join_names, normalize_name, split_names)
from work_flux.models import StatusControl


DATA = Path(__file__).resolve().parents[2] / "data"
DEFAULT_PATH = DATA / "inpi_pueblos_2025-02-21.json"


def default_states_path() -> Path | None:
    found = sorted(DATA.glob("inpi_pueblos_estados_*.json"))
    return found[-1] if found else None


def single_form(name: str) -> bool:
    return " o " not in name and "/" not in name


class Command(BaseCommand):
    help = (
        "Carga el Catálogo Nacional de Pueblos Indígenas y Afromexicanos "
        "del INPI en IndigenousGroup, con is_official=True, y sus estados "
        "desde el catálogo de comunidades del micrositio. Idempotente; "
        "nunca quita un estado, y de los nombres alternativos solo quita "
        "los que repiten el nombre o una de sus partes. Después van "
        "tidy_indigenous_groups y merge_indigenous_groups. El índice del "
        "mapa (rebuild_map_index) no incluye pueblos: no hay que "
        "reconstruirlo.")

    def add_arguments(self, parser):
        parser.add_argument("--path", default=str(DEFAULT_PATH))
        parser.add_argument(
            "--states-path", default=None,
            help="JSON pueblo → estados; por omisión el más reciente de "
                 "classify/data/inpi_pueblos_estados_*.json. «none» para "
                 "no tocar estados.")
        parser.add_argument(
            "--name-source", choices=["canonical", "dof", "microsite"],
            default="canonical",
            help="canonical: «name» del JSON, «Autodenominación "
                 "(Denominación DOF)» —Wixárika (Huichol)—; dof: la "
                 "denominación del DOF sola (Huichol); microsite: nombre "
                 "del micrositio del INPI.")
        parser.add_argument("--status", default="validated")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Corre todo dentro de una transacción y la revierte.")

    def handle(self, *args, **opts):
        path = Path(opts["path"])
        if not path.exists():
            raise CommandError(f"No existe {path}")
        pueblos = json.loads(path.read_text(encoding="utf-8"))["pueblos"]
        states_by_pueblo = self.read_states(opts["states_path"])
        status = StatusControl.objects.filter(
            name=opts["status"], group_id="validation").first()
        if not status:
            raise CommandError(
                f"No hay StatusControl de validación «{opts['status']}»")

        with transaction.atomic():
            summary = self.load(
                pueblos, opts["name_source"], status, states_by_pueblo)
            if opts["dry_run"]:
                transaction.set_rollback(True)

        for line in summary["lines"]:
            self.stdout.write(line)
        prefix = "[dry-run, revertido] " if opts["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(
            f"{prefix}{len(pueblos)} pueblos: {summary['created']} creados, "
            f"{summary['adopted']} adoptados ({summary['changed']} con "
            f"cambios), {summary['skipped']} omitidos por ambigüedad, "
            f"{summary['states']} estados agregados"))

    def read_states(self, option) -> dict | None:
        if option == "none":
            return None
        path = Path(option) if option else default_states_path()
        if not path:
            return None
        if not path.exists():
            raise CommandError(f"No existe {path}")
        data = json.loads(path.read_text(encoding="utf-8"))["pueblos"]
        by_name = {normalize_name(s.name): s for s in State.objects.all()}
        by_name.update({
            normalize_name(s.short_name): s
            for s in State.objects.exclude(short_name=None)})
        result = {}
        for dof_name, entry in data.items():
            states = []
            for state_name in entry["states"]:
                state = by_name.get(normalize_name(state_name))
                if not state:
                    # El INPI escribe el nombre oficial largo («Querétaro
                    # Arteaga»); el catálogo del INEGI, el corto.
                    longer = [s for key, s in by_name.items() if
                              normalize_name(state_name).startswith(f"{key} ")]
                    state = longer[0] if len(longer) == 1 else None
                if not state:
                    raise CommandError(
                        f"Estado desconocido «{state_name}» ({dof_name})")
                states.append(state)
            result[dof_name] = states
        return result

    def load(self, pueblos, name_source, status, states_by_pueblo):
        existing = list(
            IndigenousGroup.objects.annotate(n_actors=Count("actors")))
        summary = {"created": 0, "adopted": 0, "changed": 0, "skipped": 0,
                   "states": 0, "lines": []}
        for pueblo in pueblos:
            name, alternatives = self.names_of(pueblo, name_source)
            matches = self.find(existing, pueblo, name)
            if len(matches) > 1:
                summary["skipped"] += 1
                listed = ", ".join(f"#{g.id} {g.name}" for g in matches)
                summary["lines"].append(
                    f"OMITIDO {name}: varias entradas coinciden ({listed})")
                continue
            if matches:
                group = matches[0]
                old_name = group.name
                before = (group.name, group.alternative_names,
                          group.is_official, group.status_validation_id)
                group.name = name
                # Lo capturado antes se conserva, y el nombre viejo también,
                # salvo lo que ya dice el nombre nuevo.
                group.alternative_names = join_names(
                    alternatives + split_names(before[1]) + [old_name],
                    exclude=name) or None
                group.is_official = True
                group.status_validation = status
                changed = before != (
                    group.name, group.alternative_names, group.is_official,
                    group.status_validation_id)
                if changed:
                    group.save()
                    summary["changed"] += 1
                summary["adopted"] += 1
                summary["lines"].append(
                    f"ADOPTADO #{group.id} «{old_name}» → «{name}» "
                    f"({group.n_actors} actores)"
                    f"{'' if changed else ' sin cambios'}")
            else:
                group = IndigenousGroup.objects.create(
                    name=name, alternative_names=join_names(
                        alternatives, exclude=name) or None,
                    is_official=True, status_validation=status)
                group.n_actors = 0
                existing.append(group)
                summary["created"] += 1
                summary["lines"].append(f"CREADO #{group.id} «{name}»")
            if states_by_pueblo is not None:
                summary["states"] += self.add_states(
                    group, states_by_pueblo.get(pueblo["dof_name"], []))
        return summary

    @staticmethod
    def add_states(group, states) -> int:
        current = set(group.states.values_list("id", flat=True))
        missing = [s for s in states if s.id not in current]
        if missing:
            group.states.add(*missing)
        return len(missing)

    @staticmethod
    def find(existing, pueblo, name) -> list:
        # Adopta la entrada homónima del nombre o de una de sus dos partes
        # (la autodenominación elegida y la denominación del DOF), o del
        # nombre del micrositio cuando es una sola forma. Las demás
        # autodenominaciones no adoptan: llevar sus actores al pueblo es
        # una fusión, y la decide merge_indigenous_groups.
        tiers = [name, pueblo["name"], pueblo.get("autonym"),
                 pueblo["dof_name"]]
        if single_form(pueblo["microsite_name"]):
            tiers.append(pueblo["microsite_name"])
        for form in filter(None, tiers):
            matches = [g for g in existing
                       if normalize_name(g.name) == normalize_name(form)]
            official = [g for g in matches if g.is_official]
            if official or matches:
                return official or matches
        return []

    @staticmethod
    def names_of(pueblo, name_source) -> tuple[str, list[str]]:
        names = {
            "canonical": pueblo["name"],
            "dof": pueblo["dof_name"],
            "microsite": pueblo["microsite_name"],
        }
        name = names[name_source]
        alternatives = [pueblo["name"]] + pueblo["alternative_names"]
        return name, [a for a in alternatives
                      if normalize_name(a) != normalize_name(name)]
