from project.models import Project
from work_flux.models import StatusControl

originals = [
    (4, "filled"),
    (8, "filled"),
    (117, "filled"),
    (140, "initial"),
    (147, "initial"),
    (178, "initial"),
    (188, "filled"),
    (272, "migrated_v1"),
    (345, "initial_v1"),
    (543, "initial"),
    (553, "initial"),
    (556, "finished"),
    (561, "finished"),
    (568, "initial"),
    (584, "initial_v1"),
    (600, "initial"),
    (607, "finished"),
    (637, "Aproximado"),
    (698, "finished"),
    (704, "finished"),
    (712, "initial"),
    (761, "initial"),
    (828, "initial_v1"),
    (835, "empty"),
    (852, "need_fix"),
    (862, "initial_v1"),
    (874, "initial"),
    (876, "need_fix"),
    (877, "finished"),
    (878, "need_fix"),
    (913, "initial_v1"),
    (919, "initial_v1"),
    (926, "need_fix"),
    (999, "finished"),
    (1004, "initial_v1"),
    (1022, "need_fix"),
    (1024, "initial"),
    (1043, "filled"),
    (1055, "filled"),
    (1137, "need_fix"),
    (1138, "initial"),
    (1139, "empty"),
    (1197, "initial"),
    (1207, "initial"),
    (1233, "initial"),
    (1241, "filled"),
    (1242, "initial_v1"),
    (1243, "initial_v1"),
    (1244, "initial_v1"),
    (1246, "initial_v1"),
    (1248, "initial"),
    (1249, "initial"),
    (1290, "need_fix"),
    (1308, "initial"),
    (1319, "initial"),
    (1345, "initial"),
    (1351, "initial_v1"),
    (1364, "initial_v1"),
    (1365, "could_enhance"),
    (1385, "initial_v1"),
    (1400, "initial_v1"),
    (1406, "initial_v1"),
    (1430, "initial"),
    (1433, "initial"),
    (1482, "finished"),
    (1507, "initial"),
    (1521, "initial"),
    (1540, "initial"),
    (1581, "initial"),
    (1644, "initial"),
    (1672, "filled"),
    (1673, "filled"),
    (1680, "initial"),
    (1688, "initial"),
    (1709, "migrated_v1"),
    (1759, "filled"),
    (1788, "filled"),
    (1824, "initial"),
    (1895, "finished"),
    (1897, "initial"),
    (1930, "empty"),
    (1937, "empty"),
    (1952, "empty"),
    (1970, "empty"),
    (1974, "empty"),
    (1977, "empty"),
    (1978, "empty"),
    (1979, "empty"),
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

