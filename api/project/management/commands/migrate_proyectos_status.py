from django.core.management.base import BaseCommand
from project.models import Project


class Command(BaseCommand):
    help = 'Migracion de Status Projects'

    def handle(self, *args, **options):
        print('Migrando Status Projects')
        for project in Project.objects.all():
            _ = project.get_last_status_project(save=True)

        print('Migrando Estatus Proyectos')
