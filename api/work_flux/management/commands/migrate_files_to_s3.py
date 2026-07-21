"""Migra los archivos de NoteFile y ProjectFile del disco local a S3.

Uso (en el servidor, una sola vez por fase):

    python manage.py migrate_files_to_s3 --dry-run   # reporte previo
    python manage.py migrate_files_to_s3             # subida real
    python manage.py migrate_files_to_s3 --verify    # BD vs S3 (fase 3)

Idempotente: salta archivos ya subidos con el mismo tamaño. Instancia
el backend S3 directamente (ignora USE_S3_FILES) para poder copiar todo
ANTES de encender el flag y evitar una ventana de 404s en el switch.

Vive en work_flux (app transversal) porque api/ no está en
INSTALLED_APPS y Django solo descubre comandos de apps registradas.
"""
import json
import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from storages.backends.s3 import S3Storage

from project.models import ProjectFile
from source.models import NoteFile

MEDIA_PREFIXES = ("note_file", "project_file")


def build_s3_storage() -> S3Storage:
    return S3Storage(
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
        region_name=settings.AWS_S3_REGION_NAME,
        location=settings.AWS_LOCATION,
        default_acl=None,
        querystring_auth=False,
        # la migración replica keys exactas, sin sufijos anti-colisión
        file_overwrite=True,
        object_parameters={"StorageClass": "INTELLIGENT_TIERING"},
    )


def list_s3_sizes(storage: S3Storage) -> dict[str, int]:
    """Mapa name -> tamaño de todo lo ya subido bajo AWS_LOCATION.

    Un solo listado paginado en vez de un HEAD por archivo: ~6
    peticiones para ~5,700 objetos.
    """
    client = storage.connection.meta.client
    prefix = f"{settings.AWS_LOCATION}/"
    sizes: dict[str, int] = {}
    paginator = client.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix=prefix)
    for page in pages:
        for obj in page.get("Contents", []):
            sizes[obj["Key"][len(prefix):]] = obj["Size"]
    return sizes


class Command(BaseCommand):
    help = (
        "Sube a S3 los archivos existentes de NoteFile y ProjectFile. "
        "Idempotente; con --verify solo compara BD vs S3."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Solo reporta qué subiría, sin tocar S3")
        parser.add_argument(
            "--verify", action="store_true",
            help="Solo verifica existencia y tamaño en S3 de cada "
                 "archivo registrado en BD")
        parser.add_argument(
            "--limit", type=int, default=None,
            help="Procesa solo los primeros N archivos (pruebas)")
        parser.add_argument(
            "--report", default="migrate_s3_report.json",
            help="Ruta del JSON con el detalle por archivo")

    def handle(self, *args, **options) -> None:
        storage = build_s3_storage()
        all_names = self.get_db_file_names()
        names = all_names[:options["limit"]] if options["limit"] \
            else all_names
        s3_sizes = list_s3_sizes(storage)
        self.stdout.write(
            f"{len(all_names)} archivos en BD | "
            f"{len(s3_sizes)} objetos ya en S3")

        results: dict[str, list] = {
            "uploaded": [], "skipped": [], "missing_local": [],
            "missing_s3": [], "size_mismatch": [], "failed": [],
        }
        for idx, name in enumerate(names, start=1):
            self.process_one(name, storage, s3_sizes, options, results)
            if idx % 500 == 0:
                self.stdout.write(f"... {idx}/{len(names)}")

        # los huérfanos se detectan contra la BD completa, aunque se
        # procese un subconjunto con --limit
        results["orphans"] = self.find_orphans(set(all_names))
        self.write_report(results, options)

    def get_db_file_names(self) -> list[str]:
        note_names = NoteFile.objects.exclude(file="") \
            .values_list("file", flat=True)
        project_names = ProjectFile.objects.exclude(file="") \
            .values_list("file", flat=True)
        # dict.fromkeys: dedup preservando orden (dos registros pueden
        # apuntar al mismo archivo)
        return list(dict.fromkeys(list(note_names) + list(project_names)))

    def process_one(
            self, name: str, storage: S3Storage, s3_sizes: dict[str, int],
            options: dict, results: dict[str, list],
    ) -> None:
        local_path = os.path.join(settings.MEDIA_ROOT, name)
        local_size = os.path.getsize(local_path) \
            if os.path.exists(local_path) else None
        s3_size = s3_sizes.get(name)

        if options["verify"]:
            if s3_size is None:
                results["missing_s3"].append(name)
            elif local_size is not None and local_size != s3_size:
                results["size_mismatch"].append(
                    {"name": name, "local": local_size, "s3": s3_size})
            else:
                results["skipped"].append(name)
            return

        if local_size is None:
            results["missing_local"].append(name)
            return
        if s3_size == local_size:
            results["skipped"].append(name)
            return
        if options["dry_run"]:
            results["uploaded"].append(name)
            return
        try:
            with open(local_path, "rb") as fh:
                storage.save(name, File(fh))
            results["uploaded"].append(name)
        except Exception as exc:
            results["failed"].append({"name": name, "error": str(exc)})

    def find_orphans(self, known: set[str]) -> list[str]:
        """Archivos en disco bajo note_file/ y project_file/ sin
        registro en BD. Informativo: no se suben ni se borran."""
        orphans = []
        for prefix in MEDIA_PREFIXES:
            root = os.path.join(settings.MEDIA_ROOT, prefix)
            for dirpath, _dirs, files in os.walk(root):
                for fname in files:
                    full = os.path.join(dirpath, fname)
                    rel = os.path.relpath(full, settings.MEDIA_ROOT)
                    rel = rel.replace(os.sep, "/")
                    if rel not in known:
                        orphans.append(rel)
        return orphans

    def write_report(self, results: dict[str, list], options: dict) -> None:
        mode = "verify" if options["verify"] \
            else "dry-run" if options["dry_run"] else "upload"
        summary = {key: len(values) for key, values in results.items()}
        with open(options["report"], "w", encoding="utf-8") as fh:
            json.dump(
                {"mode": mode, "summary": summary, "detail": results},
                fh, ensure_ascii=False, indent=2)
        self.stdout.write(self.style.SUCCESS(
            f"[{mode}] " + " | ".join(
                f"{key}: {count}" for key, count in summary.items())))
        self.stdout.write(f"Detalle en {options['report']}")
