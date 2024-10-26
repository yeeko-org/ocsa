import os
import shutil
import json
import random
import hashlib

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import DataError

from project.models import Project, ProjectFile


class Command(BaseCommand):
    help = 'Move files to their corresponding Project directory and handle duplicates by adding a unique identifier.'

    def add_arguments(self, parser):

        parser.add_argument(
            '--source', type=str, help='Directory to search for files', default='media/old_files')
        parser.add_argument(
            '--output', type=str, help='Output JSON file path', default='migrate_files_exit.json')

    def handle(self, *args, **options):
        self.source_folder = options['source']
        self.output_json = options['output']
        self.media_root = settings.MEDIA_ROOT

        self.unreferenced_files = []
        self.projects_without_files = []

        self.list_all_files()

        all_projects = Project.objects.all()
        for project in all_projects:
            if not project.files.exists():
                self.projects_without_files.append(project.official_name)

        result_data = {
            "unreferenced_files": self.unreferenced_files,
            "projects_without_files": self.projects_without_files,
        }

        print("unreferenced_files length: ", len(self.unreferenced_files))
        print("projects_without_files length: ",
              len(self.projects_without_files))

        with open(self.output_json, 'w') as json_file:
            json.dump(result_data, json_file, indent=4)

        self.stdout.write(self.style.SUCCESS(
            "Proceso completado. Revisa el archivo JSON para detalles."))

    def list_all_files(self):
        for root, dirs, files in os.walk(self.source_folder):
            for filename in files:

                file_path = os.path.join(root, filename)

                self.process_file(file_path, filename)

    def process_file(self, full_path, filename):
        file_name, file_ext = os.path.splitext(filename)
        if not isinstance(file_name, str) or not file_name:
            return

        try:
            project = self.find_project(file_name)
        except Project.DoesNotExist:
            self.unreferenced_files.append(full_path)
            return
        except Project.MultipleObjectsReturned:
            self.unreferenced_files.append({
                "full_path": full_path,
                "error": "Múltiples notas encontradas."
            })
            return
        except Exception as e:
            self.unreferenced_files.append({
                "full_path": full_path,
                "error": str(e)
            })
            return

        self.relate_file_to_project(full_path, project)

    def relate_file_to_project(self, file_path, project):
        file_name_ext = os.path.basename(file_path)
        file_name, file_ext = os.path.splitext(file_name_ext)

        destination_dir = os.path.join(
            self.media_root, f'project_file/{project.pk}')
        os.makedirs(destination_dir, exist_ok=True)

        destination_file = os.path.join(destination_dir, file_name_ext)
        if os.path.exists(destination_file):

            unique_suffix = self.generate_unique_suffix(file_name_ext)
            new_filename = f"{file_name}_{unique_suffix}{file_ext}"
            destination_file = os.path.join(
                destination_dir, new_filename)
            print(
                f"Archivo duplicado encontrado. Guardando como: {new_filename}")
        try:
            ProjectFile.objects.create(project=project, file=os.path.join(
                f'project_file/{project.pk}', os.path.basename(destination_file)))
        except DataError as e:
            self.unreferenced_files.append({
                "full_path": file_path,
                "error": str(e),
                "new_path": os.path.join(
                    f'project_file/{project.pk}', os.path.basename(destination_file))
            })
            return

        shutil.move(file_path, destination_file)

    def find_project(self, file_name: str) -> Project:
        return Project.objects.get(nota_id_ref=int(file_name))

    def generate_unique_suffix(self, filename):
        """Genera un sufijo único para evitar archivos duplicados."""

        random_int = random.randint(1000, 9999)
        hash_object = hashlib.md5(filename.encode())
        unique_hash = hash_object.hexdigest()[:6]
        return f"{random_int}_{unique_hash}"
