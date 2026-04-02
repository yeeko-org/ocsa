from ps_schema.models import Collection
from ps_schema.registry import collection_registry


class InitCollections:
    """
    Crea o actualiza los registros de Collection en la DB.
    Solo aplica a CollectionSchema (primary / secondary / relational).
    Los campos editables (icon, color) solo se fijan en la primera creación
    para preservar cambios realizados desde el frontend.
    """

    def __init__(self):
        order = 0
        for _app, data in collection_registry.iter_collection_data():
            order += 1
            collection, is_new = Collection.objects.get_or_create(
                snake_name=data['snake_name'],
                defaults={
                    'level': data['level'],
                    'order': order,
                    'icon': data.get('icon'),
                    'color': data.get('color'),
                },
            )
            if not is_new:
                collection.level = data['level']
                collection.save(update_fields=['level'])