from project.models import Project
from work_flux.models import StatusControl

originals = [
    (4, "finished"),
    (8, "finished"),
    (117, "initial"),
    (140, "finished"),
    (147, "finished"),
    (178, "finished"),
    (188, "finished"),
    (272, "finished"),
    (345, "finished"),
    (543, "filled"),
    (553, "filled"),
    (556, "initial"),
    (561, "filled"),
    (568, "filled"),
    (584, "need_consensus"),
    (600, "need_consensus"),
    (607, "filled"),
    (637, "finished"),
    (698, "filled"),
    (704, "initial"),
    (712, "filled"),
    (761, "finished"),
    (828, "finished"),
    (835, "finished"),
    (852, "finished"),
    (862, "finished"),
    (874, "filled"),
    (876, "finished"),
    (877, "filled"),
    (878, "filled"),
    (913, "finished"),
    (919, "finished"),
    (926, "filled"),
    (999, "initial"),
    (1004, "finished"),
    (1022, "finished"),
    (1024, "need_consensus"),
    (1043, "finished"),
    (1055, "need_consensus"),
    (1137, "finished"),
    (1138, "filled"),
    (1139, "filled"),
    (1197, "finished"),
    (1207, "finished"),
    (1233, "filled"),
    (1241, "finished"),
    (1242, "finished"),
    (1243, "finished"),
    (1244, "finished"),
    (1246, "finished"),
    (1248, "filled"),
    (1249, "filled"),
    (1290, "initial"),
    (1308, "filled"),
    (1319, "filled"),
    (1345, "filled"),
    (1351, "finished"),
    (1364, "finished"),
    (1365, "initial"),
    (1385, "filled"),
    (1400, "filled"),
    (1406, "finished"),
    (1430, "filled"),
    (1433, "filled"),
    (1482, "filled"),
    (1507, "finished"),
    (1521, "filled"),
    (1540, "finished"),
    (1581, "finished"),
    (1644, "finished"),
    (1672, "finished"),
    (1673, "finished"),
    (1680, "finished"),
    (1688, "filled"),
    (1709, "filled"),
    (1759, "finished"),
    (1788, "finished"),
    (1824, "finished"),
    (1895, "filled"),
    (1897, "filled"),
    (1930, "initial"),
    (1937, "initial"),
    (1952, "initial_v1"),
    (1970, "initial_v1"),
    (1974, "initial"),
    (1977, "initial"),
    (1978, "initial"),
    (1979, "initial"),
]


def apply_incongruent() -> None:
    """Marca como incongruentes los proyectos de ``originals`` y guarda
    el ``public_name`` del StatusControl correspondiente en
    ``prev_status_loc`` (resuelto a partir de su ``name``)."""
    names = {name for _, name in originals}
    status_map = dict(
        StatusControl.objects
        .filter(name__in=names)
        .values_list("name", "public_name"))

    missing_status = names - status_map.keys()
    if missing_status:
        print(f"StatusControl no encontrados: {sorted(missing_status)}")

    projects = Project.objects.in_bulk([pid for pid, _ in originals])

    to_update = []
    missing_projects = []
    for pid, name in originals:
        project = projects.get(pid)
        if project is None:
            missing_projects.append(pid)
            continue
        project.incongruent = True
        project.prev_status_loc = status_map.get(name)
        to_update.append(project)

    if missing_projects:
        print(f"Proyectos no encontrados: {missing_projects}")

    Project.objects.bulk_update(
        to_update, ["incongruent", "prev_status_loc"])
    print(f"{len(to_update)} proyectos actualizados.")

