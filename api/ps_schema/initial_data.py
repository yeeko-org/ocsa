from ps_schema.models import Level, Collection, CollectionLink, FilterGroup
from ps_schema.constants import all_collections, collection_links, filter_groups


class InitLevels:

    def __init__(self):
        init_levels = (
            ('primary', 'Colección principal', '0'),
            ('secondary', 'Colección secundaria', '1'),
            ('relational', 'Colección relacional', '2'),
            ('category_group', 'Grupo de categorías', '3'),
            ('category_type', 'Tipo de categoría', '4'),
            ('category_subtype', 'Subtipo de categoría', '5'),
        )
        for key_name, name, order in init_levels:
            Level.objects.get_or_create(
                key_name=key_name,
                defaults=dict(
                    name=name,
                    order=order
                )
            )


class InitCollections:

    def __init__(self):
        levels_dict = {level.key_name: level for level in Level.objects.all()}
        # Collection.objects.all().delete()
        order_base = 0
        order = 0
        for app_label, collections in all_collections.items():
            for collection in collections:
                order += 1
                new_collection, _ = Collection.objects.get_or_create(
                    snake_name=collection['snake_name'],
                    level=levels_dict[collection['level']],
                    app_label=app_label)
                new_collection.name = collection['name']
                new_collection.plural_name = collection['plural_name']
                new_collection.model_name = collection['model_name']
                new_collection.status_group = collection.get('status_group', None)
                new_collection.optional_category = collection.get('optional_category', False)
                new_collection.icon = collection.get('icon', None)
                new_collection.color = collection.get('color', None)
                new_collection.order = order_base + order
                new_collection.all_filters = collection.get('all_filters', [])
                new_collection.save()
                # print(f"Order: {order_base + order}\n{defaults}")
            order_base += 10


class InitFilterGroups:
    def __init__(self):
        # FilterGroup.objects.all().delete()
        collections_dict = {
            f"{collection.app_label}-{collection.snake_name}": collection
            for collection in Collection.objects.all()}
        print("collections_dict", collections_dict)
        for group in filter_groups:
            # category_group = group.get('category_group', None)
            # print("category_group", category_group)
            # print("collection_group", collections_dict.get(category_group, None))
            filter_group, _ = FilterGroup.objects.get_or_create(
                key_name=group['key_name'],
                defaults=dict(
                    main_collection=collections_dict.get(
                        group['main_collection'], None),
                )
            )
            filter_group.name = group.get('name', "Sin nombre")
            filter_group.plural_name = group.get('plural_name', "Sin nombre plural")
            # filter_group.main_collection = collections_dict.get(
            #     group['main_collection'], None)
            filter_group.category_group = collections_dict.get(
                group.get('category_group', None), None)
            filter_group.category_type = collections_dict.get(
                group.get('category_type', None), None)
            filter_group.category_subtype = collections_dict.get(
                group.get('category_subtype', None), None)
            filter_group.add_config = group.get('add_config', {})
            filter_group.save()
            # print("-" * 50)


class InitCollectionLinks:
    def __init__(self):
        # CollectionLink.objects.all().delete()
        collections_dict = {
            f"{collection.app_label}-{collection.snake_name}": collection
            for collection in Collection.objects.all()}
        for link in collection_links:
            filter_group_obj = None
            if filter_group := link.get('filter_group', None):
                filter_group_obj = FilterGroup.objects.get(
                    key_name=filter_group)
                print("filter_group_obj", filter_group_obj)
            cl, created = CollectionLink.objects.get_or_create(
                parent=collections_dict[link['parent']],
                child=collections_dict[link['child']],
            )
            cl.link_type = link['link_type']
            cl.is_provisional = link.get('is_provisional', False)
            cl.is_multiple = link.get('is_multiple', False)
            cl.is_mandatory = link.get('is_mandatory', False)
            cl.filter_group = filter_group_obj
            cl.save()
