from typing import Optional
from actor.models import Actor, CapitalType, Interest, Participant
from ocsa_legacy.models import Capital, EstatusProyectos, Nota, Proyecto
from project.models import Project
from source.models import Mention, Note
from space_time.models import Country, StatusProject


class CapitalToActorMigration:
    errors = []

    def __init__(self):
        capitales = Capital.objects.all()

        for capital in capitales:
            try:
                self.migrate_to_actor(capital)
            except Exception as e:
                self.errors.append([capital, e])

    def get_country(self, name):
        if not name:
            return None
        country, _ = Country.objects.get_or_create(name=name)
        return country

    def get_capital_type(self, is_public: Optional[bool] = None):
        if is_public is None:
            return None
        name = "Público" if is_public else "Privado"
        capital_type, _ = CapitalType.objects.get_or_create(name=name)
        return capital_type

    def get_actor_matriz(self, capital: Capital):
        if not capital.matriz or capital.matriz == "SD":
            return None

        parent_actor, parent_actor_created = Actor.objects\
            .get_or_create(name=capital.matriz)
        if parent_actor_created:
            parent_actor.is_only_related = True
            parent_actor.save()

        return parent_actor

    def get_actor_filial(self, capital: Capital, actor: Actor):
        if not capital.filial or capital.filial == "SD":
            return None

        filial_actor, filial_actor_created = Actor.objects\
            .get_or_create(name=capital.filial)
        if filial_actor_created:
            filial_actor.parent_actor = actor  # type: ignore
            filial_actor.save()

        return filial_actor

    def get_capital_extension(self, capital: Capital):
        capital_extension = {}
        if capital.directores:
            capital_extension['directores'] = capital.directores
        if capital.inversionistas:
            capital_extension['inversionistas'] = capital.inversionistas
        if capital.is_cotiza_bolsa is not None:
            capital_extension['is_cotiza_bolsa'] = capital.is_cotiza_bolsa
        return capital_extension

    def get_status_project(self, capital: Capital):

        ### para Ricardo

        # Existen varios registros de EstatusProyectos con la misma nota y proyecto
        # analizar si cual va dependiendo de la temporalidad?
        # migracion temporal: ordenar por id y tomar el ultimo

        estatus_proyecto = EstatusProyectos.objects.filter(
            nota=capital.nota, proyecto=capital.proyecto).order_by('id').last()
        if not estatus_proyecto:
            return None

        if estatus_proyecto.estatus and estatus_proyecto.estatus.nombre:
            status_project, _ = StatusProject.objects.get_or_create(
                name=estatus_proyecto.estatus.nombre,
            )
            return status_project

    def create_mention(self, capital: Capital, actor: Actor):

        if not (capital.nota and capital.proyecto):
            return

        status_project = self.get_status_project(capital)
        note = Note.objects.filter(pk=capital.nota.pk).first()
        project = Project.objects.filter(
            proyecto_id_ref=capital.proyecto.pk).first()

        if not (note and project):
            return

        mention = Mention.objects.create(
            note=note,
            project=project,
            status_project=status_project,
        )

        # participant_types?
        participant = Participant.objects.create(
            actor=actor,
            mention=mention,
        )

        # create Interest
        if capital.interes and capital.interes != "SD":
            Interest.objects.create(
                participant=participant,
                text=capital.interes,
            )

    def migrate_to_actor(self, capital: Capital):
        #### Para Ricardo

        # analizar caso capital.pk = 1647 y capital.nombre = 'Grupo Vidanta'
        # 1647 no tiene nombre pero si matriz y director
        # 'Grupo Vidanta' se encuentra varias veces en capital lo que deveria reflejar
        # un mismo actor, y generar las diferentes menciones, pero tiene una muy ligera
        # variacion de datos en director, para este caso, el primer registro guarda
        # la informacion de director y los siguientes ignoran las variantes
        # que pasara cuando las variantes sean muy notorias? como matricez o filiales diferentes
        # Nota: No es caso aislado, existen muchos otros casos similares

        actor, _ = Actor.objects\
            .get_or_create(name=capital.filial)

        if not actor.capital_id_ref:

            actor.parent_actor = self.get_actor_matriz(capital)  # type: ignore
            actor.capital_extension = self.get_capital_extension(  # type: ignore
                capital)
            actor.capital_type = self.get_capital_type(
                capital.is_capital_publico)
            actor.save()

            country = self.get_country(capital.nacionalidad)
            if country:
                actor.countries.add(country)

            _ = self.get_actor_filial(capital, actor)

        self.create_mention(capital, actor)
