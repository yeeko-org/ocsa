from api.export_blocks.base import ExportBlock


class LocationExportBlock(ExportBlock):
    """Columnas y extractor para la ubicación principal de una entidad.

    Requiere que el queryset haya sido anotado con get_annotations().
    Los valores se leen de los atributos ORM anotados en el objeto.
    """

    columns = [
        {"name": "ID de ubicación principal", "width": 5, "field": "location_id"},
        {"name": "ID de Entidad", "width": 4, "field": "state__inegi_code"},
        {"name": "Entidad", "width": 25, "field": "state__short_name"},
        {"name": "ID de Municipio", "width": 4,
         "field": "municipality__inegi_code"},
        {"name": "Municipio", "width": 25, "field": "municipality__name"},
        {"name": "ID de Localidad", "width": 4,
         "field": "locality__inegi_code"},
        {"name": "Localidad", "width": 25, "field": "locality__name"},
        {"name": "Latitud", "width": 12, "field": "latitude"},
        {"name": "Longitud", "width": 12, "field": "longitude"},
    ]

    # Campos que get_annotations() debe anotar en el queryset
    annotation_fields: list[str] = [
        'state__inegi_code', 'state__short_name',
        'municipality__inegi_code', 'municipality__name',
        'locality__inegi_code', 'locality__name',
        'latitude', 'longitude',
    ]

    @classmethod
    def extract(cls, obj) -> dict:
        """Lee los valores de las anotaciones ORM del objeto.

        Devuelve un dict anidado compatible con el traversal __ de
        ExportXlsMixin: state__inegi_code → row['state']['inegi_code'].
        """
        return {
            "location_id": getattr(obj, 'location_id', None),
            "state": {
                "inegi_code": getattr(obj, 'state__inegi_code', None),
                "short_name": getattr(obj, 'state__short_name', None),
            },
            "municipality": {
                "inegi_code": getattr(
                    obj, 'municipality__inegi_code', None),
                "name": getattr(obj, 'municipality__name', None),
            },
            "locality": {
                "inegi_code": getattr(obj, 'locality__inegi_code', None),
                "name": getattr(obj, 'locality__name', None),
            },
            "latitude": getattr(obj, 'latitude', None),
            "longitude": getattr(obj, 'longitude', None),
        }