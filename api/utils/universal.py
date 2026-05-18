def nombre_or_pk(obj, pk, attr='nombre'):
    name = getattr(obj, attr, None) or pk
    return str(name)


def camel_to_snake(name):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def compute_project_status_location(project) -> str:
    """
    Devuelve el status_location que le corresponde al Project según
    sus Locations. Criterio: el StatusControl con priority más alta
    (peor) domina. Sin Locations con status: 'empty'.
    """
    worst_id = (
        project.locations
        .filter(status_location__isnull=False)
        .order_by('-status_location__priority')
        .values_list('status_location_id', flat=True)
        .first())
    return worst_id or 'empty'


def apply_project_status_location(
        project, save: bool = True) -> tuple[str | None, str]:
    """
    Sincroniza Project.status_location con el valor calculado.
    Retorna (antes, después) para registrar la transición.
    """
    previous = project.status_location_id
    computed = compute_project_status_location(project)
    if previous != computed:
        project.status_location_id = computed
        if save:
            project.save(update_fields=['status_location'])
    return previous, computed
