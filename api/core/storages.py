"""Selección de storage para archivos de documentos (alias "docs").

Al pasarse como callable a FileField, la migración serializa la
referencia a la función, no el backend resuelto: cambiar el backend
por entorno (S3 en producción, disco en local) no genera migraciones.
"""
from django.core.files.storage import Storage, storages


def select_docs_storage() -> Storage:
    """Devuelve el storage del alias "docs" según STORAGES."""
    return storages["docs"]
