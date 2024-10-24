import os
import shutil
import json
import random
import hashlib
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import DataError

from source.models import Note, NoteFile, clean_text


class Command(BaseCommand):
    help = 'Move files to their corresponding Note directory and handle duplicates by adding a unique identifier.'

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
        self.notes_without_files = []

        for note in Note.objects.filter(slug_title__isnull=True):
            note.set_slug_title(save=True)

        self.list_all_files()

        all_notes = Note.objects.all()
        for note in all_notes:
            if not note.files.exists():
                self.notes_without_files.append(note.title)

        result_data = {
            "unreferenced_files": self.unreferenced_files,
            "notes_without_files": self.notes_without_files,
        }

        print("unreferenced_files length: ", len(self.unreferenced_files))
        print("notes_without_files length: ", len(self.notes_without_files))

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
            note = self.find_note(file_name)
        except Note.DoesNotExist:
            self.unreferenced_files.append(full_path)
            return
        except Note.MultipleObjectsReturned:
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

        destination_dir = os.path.join(
            self.media_root, f'note_file/{note.pk}')
        os.makedirs(destination_dir, exist_ok=True)

        destination_file = os.path.join(destination_dir, filename)
        if os.path.exists(destination_file):

            unique_suffix = self.generate_unique_suffix(filename)
            new_filename = f"{file_name}_{unique_suffix}{file_ext}"
            destination_file = os.path.join(
                destination_dir, new_filename)
            print(
                f"Archivo duplicado encontrado. Guardando como: {new_filename}")
        try:
            NoteFile.objects.create(note=note, file=os.path.join(
                f'note_file/{note.pk}', os.path.basename(destination_file)))
        except DataError as e:
            self.unreferenced_files.append({
                "full_path": full_path,
                "error": str(e),
                "new_path": os.path.join(
                    f'note_file/{note.pk}', os.path.basename(destination_file))
            })
            return

        shutil.move(full_path, destination_file)

    def find_note(self, file_name: str) -> Note:
        if file_name.isdigit():
            return Note.objects.get(nota_id_ref=int(file_name))

        note = self.find_note_by_title(file_name)
        if note:
            return note

        raise Note.DoesNotExist("Nota no encontrada.")

    def find_note_by_title(self, title: str) -> Note:

        try:
            return Note.objects.get(title__icontains=title)
        except Note.DoesNotExist:
            pass

        try:
            return Note.objects.get(title__icontains=title.strip())
        except Note.DoesNotExist:
            pass
        try:
            return Note.objects.get(title__icontains=title.replace("La Jornada_", "").strip())
        except Note.DoesNotExist:
            pass
        
        try:
            return Note.objects.get(slug_title=clean_text(title))
        except Note.DoesNotExist:
            pass
        
        return Note.objects.get(slug_title=clean_text(title.replace("La Jornada_", "")))
        

    def generate_unique_suffix(self, filename):
        """Genera un sufijo único para evitar archivos duplicados."""

        random_int = random.randint(1000, 9999)
        hash_object = hashlib.md5(filename.encode())
        unique_hash = hash_object.hexdigest()[:6]
        return f"{random_int}_{unique_hash}"
