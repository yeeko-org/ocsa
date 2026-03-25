from rest_framework import serializers


xlsx_mention_group = [
    {
        "name": "ID de nota",
        "width": 5,
        "field": "mention__note_full__id"
    },
    {
        "name": "Fecha de nota",
        "width": 10,
        "field": "mention__note_full__date"
    },
    {
        "name": "Título de nota",
        "width": 40,
        "field": "mention__note_full__title"
    },
    {
        "name": "Medio de la nota",
        "width": 15,
        "field": "mention__note_full__source"
    },
    {
        "name": "ID de proyecto",
        "width": 5,
        "field": "mention__project_full__id"
    },
    {
        "name": "Nombre de proyecto",
        "width": 40,
        "field": "mention__project_full__name"
    },
    {
        "name": "ID de conflicto",
        "width": 5,
        "field": "conflict__id"
    },
    {
        "name": "Nombre de conflicto",
        "width": 30,
        "field": "conflict__name"
    },
]
