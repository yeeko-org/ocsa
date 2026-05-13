from collections import Counter

from utils.universal import (
    compute_project_status_location, apply_project_status_location)


def dry_run():
    """
    Recorre todos los proyectos y reporta qué pasaría al sincronizar
    Project.status_location con sus Locations. No toca la BD.
    """
    from project.models import Project
    projects = Project.objects.all().prefetch_related(
        'locations__status_location')
    total = 0
    unchanged = 0
    transitions: Counter = Counter()
    reasons: Counter = Counter()
    combinations: Counter = Counter()
    for project in projects:
        total += 1
        previous = project.status_location_id
        computed = compute_project_status_location(project)
        if previous == computed:
            unchanged += 1
            continue
        transitions[(previous, computed)] += 1
        n_locs = len(project.locations.all())
        if n_locs == 0:
            reasons['sin_locations'] += 1
        elif n_locs == 1:
            reasons['una_location'] += 1
        else:
            reasons['varias_locations'] += 1
            status_ids = [
                loc.status_location_id for loc in project.locations.all()
                if loc.status_location_id]
            combo = frozenset(status_ids)
            combinations[(combo, previous, computed)] += 1
        if previous is None:
            reasons['actual_era_null'] += 1
    changed = total - unchanged
    print(f"Proyectos revisados: {total}")
    print(f"Sin cambios:         {unchanged}")
    print(f"Cambiarian:          {changed}")
    print()
    print("Transiciones (actual -> nuevo) por frecuencia:")
    for (before, after), count in transitions.most_common():
        before_s = repr(before)
        after_s = repr(after)
        print(f"  {before_s:>20} -> {after_s:<20} {count}")
    print()
    print("Razones (categorias, no excluyentes):")
    for reason, count in reasons.most_common():
        print(f"  {reason:<20} {count}")
    print()
    print("Combinaciones (>1 ubicacion) que disparan cambio:")
    for (combo, previous, new_status), count in combinations.most_common():
        combo_display = '{' + ', '.join(
            f"'{s}'" for s in sorted(combo)) + '}'
        print(f"  {combo_display} || {previous} -> {new_status!r}   {count}")


def run():
    """Aplica la sincronizacion a todos los proyectos."""
    from project.models import Project
    projects = Project.objects.all().prefetch_related('locations')
    changed = 0
    for project in projects:
        previous, computed = apply_project_status_location(project)
        if previous != computed:
            changed += 1
    print(f"Proyectos actualizados: {changed}")