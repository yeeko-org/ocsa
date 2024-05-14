import traceback
from django.core.management.base import BaseCommand

from actor.migrate.grupos_apoyo import GruposApoyoToActorMigration
from actor.migrate.poblacion_afectada import PoblacionAfectadaToActorMigration
from actor.migrate.status_project import MigrateStatusProject
from actor.migrate import (
    CapitalToActorMigration, EstadoToActorMigration, OpositorToActorMigration)
from actor.models import Actor


class Command(BaseCommand):
    help = 'Migración de Modelos Legacy a Actors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-old-actors',
            type=bool,
            help='Delete old actors after migration',
        )

    def handle(self, *args, **kwargs):
        delete_old_actors = kwargs.get('delete_old_actors', False)

        if delete_old_actors:
            print("Deleting old actors")
            Actor.objects.all().delete()

        print("Starting StatusProject migration")
        status_project_migration = MigrateStatusProject()

        for status, error in status_project_migration.errors:
            print(f"Error with status {status.pk}: {status}")
            print(error)
            print()

        print("Starting Capital to Actor migration")
        capital_migration = CapitalToActorMigration()

        for capital, error in capital_migration.errors:
            pk = getattr(capital, "pk", None)
            print(f"Error with capital {pk}: {capital}")
            print(error)
            print()

        print("Starting Estado to Actor migration")
        estado_migration = EstadoToActorMigration()

        for estado, error in estado_migration.errors:
            print(f"Error with estado {estado.pk}: {estado}")
            print(error)
            print()

        print("Starting Opositor to Actor migration")
        opositor_migration = OpositorToActorMigration()

        for opositor, error in opositor_migration.errors:
            print(f"Error with opositor {opositor.pk}: {opositor}")
            print(error)
            print()

        print("Starting Grupos de Apoyo to Actor migration")
        ga_migration = GruposApoyoToActorMigration()

        for grupo_apoyo, error in ga_migration.errors:
            print(f"Error with grupo apoyo {grupo_apoyo.pk}: {grupo_apoyo}")
            print(error)
            print()

        print("Starting Poblaciones Afectadas to Actor migration")
        poblaciones_migration = PoblacionAfectadaToActorMigration()

        for poblacion, error in poblaciones_migration.errors:
            print(
                f"Error with poblaciones afectadas {poblacion.pk}: {poblacion}")
            print(error)
            print()
