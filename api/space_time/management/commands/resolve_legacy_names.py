"""Dictamen sobre los topónimos legados atorados en `Location.comments`.

Solo lee: recorre las ubicaciones cuyo comentario empieza con `YEEKO:`,
resuelve cada fragmento contra el catálogo del INEGI dentro del ámbito
capturado y escribe un CSV de veredictos para revisión. Aplicarlos es
trabajo del backfill, que importa el mismo `space_time/legacy_names.py`.
"""

import csv
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand

from space_time.geometry import has_geometry
from space_time.legacy_names import (
    HOMONYM, TEMPLATE_HOMONYM, TEMPLATE_LOCALITY, TEMPLATE_MUNICIPALITY,
    CandidateIndex, Match, exact_homonyms, match_legacy_name,
    parse_yeeko_fragments, type3_signal, verdict_for)
from space_time.models import Location

DEFAULT_OUT = ".claude/verdicts/legacy_names_verdicts.csv"
FIELDS = [
    "location_id", "project_id", "has_project", "has_geometry", "status",
    "template", "legacy_value", "scope_state", "scope_municipality",
    "match_level", "candidate_name", "candidate_id", "score",
    "type3_signal", "verdict", "fragment_verbatim",
]


class Command(BaseCommand):
    help = ("Dictamina los topónimos legados de `Location.comments` "
            "contra el catálogo del INEGI (solo lectura)")

    def add_arguments(self, parser):
        parser.add_argument("--out", default=DEFAULT_OUT)
        parser.add_argument(
            "--project-only", action="store_true",
            help="Solo ubicaciones ligadas a un proyecto")

    def handle(self, *args, **options):
        locations = Location.objects.filter(
            comments__startswith="YEEKO:").select_related(
            "state", "municipality").order_by("id")
        if options["project_only"]:
            locations = locations.filter(project__isnull=False)

        index = CandidateIndex()
        rows = []
        skipped = Counter()
        for location in locations:
            for fragment in parse_yeeko_fragments(location.comments):
                if not fragment.template:
                    skipped[fragment.kind] += 1
                    continue
                rows.append(self.build_row(location, fragment, index))

        out_path = Path(options["out"])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open(
                "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        self.report(rows, skipped, out_path)

    def build_row(self, location, fragment, index):
        if fragment.template == TEMPLATE_LOCALITY:
            candidates = index.localities(location.municipality_id)
        elif fragment.template == TEMPLATE_MUNICIPALITY:
            candidates = index.municipalities(location.state_id)
        else:
            # Homónimo: el ámbito es el de la capa que quedó ambigua.
            candidates = (
                index.localities(location.municipality_id)
                if fragment.kind == "locality_ambiguous"
                else index.municipalities(location.state_id))

        signal = type3_signal(fragment.value)
        if fragment.template == TEMPLATE_HOMONYM:
            homonyms = exact_homonyms(fragment.value, candidates)
            match = Match(HOMONYM, None, 0.0)
            names = " | ".join(c.name for c in homonyms)
            ids = "|".join(str(c.id) for c in homonyms)
            score = ""
        else:
            match = match_legacy_name(fragment.value, candidates)
            names = match.candidate.name if match.candidate else ""
            ids = str(match.candidate.id) if match.candidate else ""
            score = round(match.score, 2)

        return {
            "location_id": location.id,
            "project_id": location.project_id or "",
            "has_project": int(bool(location.project_id)),
            "has_geometry": int(has_geometry(location)),
            "status": location.status_location_id or "",
            "template": fragment.template,
            "legacy_value": fragment.value,
            "scope_state": (
                location.state.name if location.state_id else ""),
            "scope_municipality": (
                location.municipality.name if location.municipality_id
                else ""),
            "match_level": match.level,
            "candidate_name": names,
            "candidate_id": ids,
            "score": score,
            "type3_signal": signal,
            "verdict": verdict_for(match.level, signal, fragment.template),
            "fragment_verbatim": fragment.verbatim,
        }

    def report(self, rows, skipped, out_path):
        write = self.stdout.write
        write(f"Fragmentos dictaminados: {len(rows)}")
        if skipped:
            write("Fragmentos fuera de alcance (no se escriben): "
                  + ", ".join(f"{k}={v}" for k, v in skipped.most_common()))
        tally = Counter(
            (row["has_project"], row["template"], row["match_level"],
             row["verdict"])
            for row in rows)
        write("\nhas_project | plantilla | match_level | veredicto | n")
        for key in sorted(tally, key=lambda k: (-k[0], k[1], k[2], k[3])):
            has_project, template, level, verdict = key
            write(f"{has_project} | {template} | {level} | {verdict} | "
                  f"{tally[key]}")
        write(f"\nCSV: {out_path} ({len(rows)} filas)")
