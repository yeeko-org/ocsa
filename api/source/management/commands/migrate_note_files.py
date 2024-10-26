import os
import re
import shutil
import json
import random
import hashlib

from typing import Dict, List
from difflib import SequenceMatcher as Matcher
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
        parser.add_argument(
            '--similar_ratio', type=float, help='Minimal Ratio for similar', default=0.95)

    def handle(self, *args, **options):
        self.source_folder = options['source']
        self.output_json = options['output']
        self.similar_ratio = options['similar_ratio']
        self.media_root = settings.MEDIA_ROOT

        self.unreferenced_files = []
        self.notes_without_files = []

        for note in Note.objects.filter(slug_title__isnull=True):
            note.set_slug_title(save=True)

        self.list_all_files()

        self.find_by_similar()

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

        self.relate_file_to_note(full_path, note)

    def relate_file_to_note(self, file_path, note):
        file_name_ext = os.path.basename(file_path)
        file_name, file_ext = os.path.splitext(file_name_ext)

        destination_dir = os.path.join(
            self.media_root, f'note_file/{note.pk}')
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
            NoteFile.objects.create(note=note, file=os.path.join(
                f'note_file/{note.pk}', os.path.basename(destination_file)))
        except DataError as e:
            self.unreferenced_files.append({
                "full_path": file_path,
                "error": str(e),
                "new_path": os.path.join(
                    f'note_file/{note.pk}', os.path.basename(destination_file))
            })
            return

        shutil.move(file_path, destination_file)

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

    def find_by_similar(self):
        notes_date = NoteDate()
        unreferenced_files = []
        for file_path in self.unreferenced_files:
            if not isinstance(file_path, str):
                unreferenced_files.append(file_path)
                continue
            notes = notes_date.get_notes_by_file_path(file_path)
            if not notes:
                unreferenced_files.append(file_path)
                continue

            print(f"Procesando {file_path}, {len(notes)} notas encontradas.")
            for note in notes:
                print(note.title, note.date)

            full_file_name = os.path.basename(file_path)
            file_name, _ = os.path.splitext(full_file_name)

            note = self.get_best_match(os.path.basename(file_name), notes)
            print("Mejor coincidencia: ", note.title if note else None)
            print()
            if note:
                self.relate_file_to_note(file_path, note)
            else:
                unreferenced_files.append(file_path)

        self.unreferenced_files = unreferenced_files

    def get_best_match(self, title, notes: List[Note]):
        title = title.replace("La Jornada_", "")

        best_matchs = [
            (Matcher(None, title, note.title).ratio(), note) for note in notes]

        if not best_matchs:
            return None

        best_matchs.sort(key=lambda x: x[0], reverse=True)
        if best_matchs[0][0] > self.similar_ratio:
            return best_matchs[0][1]


class NoteDate:
    notes: Dict[int, Dict[int, List[Note]]]

    def __init__(self):
        self.notes = {}
        for note in Note.objects.filter(files__isnull=False).order_by('title'):
            if note.date.year not in self.notes:
                self.notes[note.date.year] = {}
            if note.date.month not in self.notes[note.date.year]:
                self.notes[note.date.year][note.date.month] = []
            self.notes[note.date.year][note.date.month].append(note)

    def get_notes_by_file_path(self, file_path: str):
        year, month = self.extract_year_month(file_path)
        if year is None or month is None:
            return []

        notes = self.notes.get(year, {}).get(month, [])
        if notes:
            print(f"Extrayendo notas para {year}, {month}")
            return notes

    def extract_year_month(self, file_path: str):
        meses = {
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5,
            'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Septiembre': 9,
            'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
        }

        pattern = r'(20\d{2}).*?(' + '|'.join(meses.keys()) + ')'

        match = re.search(pattern, file_path)

        if not match:
            return None, None

        year = int(match.group(1))
        month_name = match.group(2)

        month = meses[month_name]

        return year, month
