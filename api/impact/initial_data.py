from impact.models import ImpactGroup

init_impact_groups = [
    ('Social', 'group', 'teal', True),
    ('Ambiental', 'eco', 'green', False),
]


class InitialImpactGroups:

    def __init__(self):

        for name, icon, color, is_social in init_impact_groups:
            impact_group, _ = ImpactGroup.objects.get_or_create(
                name=name,
                is_social=is_social,
                defaults={'icon': icon, 'color': color}
            )
