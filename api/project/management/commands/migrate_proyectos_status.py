from django.core.management.base import BaseCommand
from project.models import Project


class Command(BaseCommand):
    help = 'Migracion de Status Projects'

    def handle(self, *args, **options):
        print('Comenzando migración Status Projects')
        for project in Project.objects.all():
            _ = project.get_last_status_project(save=True)

        print('Terminada migración Estatus Proyectos')
