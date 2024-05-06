from typing import Optional
from actor.models import Actor, CapitalType
from ocsa_legacy.models import Capital
from work_flux.models import StatusControl
from space_time.models import Country
from actor.migrate.common import text_normalizer, ActorBase


class CapitalToActorMigration(ActorBase):
    errors = []

    def __init__(self):
        super().__init__()

        capitales = Capital.objects.all()

        self.need_review, _ = StatusControl.objects.get_or_create(
            name="need_review", group="validation",
            public_name="Requiere revisión")

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

    def get_capital_extension(self, actor: Actor, capital: Capital):
        capital_extension = actor.capital_extension or {}
        fields = ["directores", "inversionistas", "is_cotiza_bolsa"]
        for field in fields:
            saved_value = capital_extension.get(field, [])
            value = getattr(capital, field)
            if value is not None:
                saved_value.append(value)
                capital_extension[field] = saved_value
        return capital_extension

    def migrate_to_actor(self, capital: Capital):
        # ### Para Ricardo

        # analizar caso capital.pk = 1647 y capital.nombre = 'Grupo Vidanta'
        # 1647 no tiene nombre pero si matriz y director
        # 'Grupo Vidanta' se encuentra varias veces en capital lo que deveria reflejar
        # un mismo actor, y generar las diferentes menciones, pero tiene una muy ligera
        # variacion de datos en director, para este caso, el primer registro guarda
        # la informacion de director y los siguientes ignoran las variantes
        # que pasara cuando las variantes sean muy notorias? como matricez o filiales diferentes
        # Nota: No es caso aislado, existen muchos otros casos similares

        # RESPUESTA: Por lo pronto hay que registrar esas inconsistencias en
        # el reporte de errores, para analizar los casos uno por uno

        # ### Para Ricardo Ya no es necesario la comprovacion con "SD"
        # def get_real_attribute(field):
        #     value = getattr(capital, field)
        #     if value == "" or value == "SD" or value is None:
        #         return None
        #     return value

        nombre = capital.nombre
        matriz = capital.matriz
        filial = capital.filial
        std_nombre = text_normalizer(nombre)
        std_matriz = text_normalizer(matriz)
        std_filial = text_normalizer(filial)

        real_count = (bool(nombre) + bool(matriz) + bool(filial))

        final_name = None
        need_review = False

        if real_count == 0:
            need_review = True
        elif real_count == 1:
            final_name = nombre or matriz or filial
        else:
            if nombre and std_nombre == std_matriz:
                nombre = None

            if nombre and std_nombre == std_filial:
                filial = None

            if matriz and std_matriz == std_filial:
                filial = None

            if nombre and not matriz and filial:
                if std_nombre != std_filial:
                    need_review = True
                    matriz = filial
                    std_matriz = std_filial
                filial = None

            real_count = (bool(nombre) + bool(matriz) + bool(filial))
            if real_count == 1:
                final_name = nombre or matriz or filial

        actor = None
        matriz_actor = None
        filial_actor = None
        if final_name:
            actor, _ = Actor.objects.get_or_create(name=final_name)
        elif real_count > 1:
            if nombre:
                actor = self.get_actor(nombre, std_nombre)
            if matriz:
                matriz_actor = self.get_actor(matriz, std_matriz)
            if filial:
                filial_actor = self.get_actor(filial, std_filial)

        if actor:
            if need_review:
                actor.status_validation = self.need_review
            if matriz_actor:
                self.add_parent(actor, matriz_actor)
            actor.save()
        if matriz_actor:
            if actor and matriz_actor.is_only_related is False:
                matriz_actor.is_only_related = True
            if need_review:
                matriz_actor.status_validation = self.need_review
            matriz_actor.save()
        if filial_actor:
            if matriz_actor:
                self.add_parent(filial_actor, matriz_actor)
            elif actor:
                self.add_parent(filial_actor, actor)
            filial_actor.is_only_related = True
            if need_review:
                filial_actor.status_validation = self.need_review
            filial_actor.save()

        main_actor = actor or matriz_actor or filial_actor
        if not main_actor:
            self.errors.append([capital, "No actor created"])
            return
        main_actor.is_only_related = False
        main_actor.capital_extension = self.get_capital_extension(  # type: ignore
            main_actor, capital)

        # actor.parent_actor = self.get_actor_matriz(capital)  # type: ignore
        # RICK: No estoy seguro de la existencia de capital_type, por ahora
        # lo dejaré comentado
        # actor.capital_type = self.get_capital_type(
        #     capital.is_capital_publico)

        country = self.get_country(capital.nacionalidad)
        if country:
            main_actor.countries.add(country)

        mention = self.get_mention(capital)
        if mention:
            self.add_participant(main_actor, mention, ["Capital"])
            self.add_status_project(mention)
        main_actor.save()
