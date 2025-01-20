from typing import Optional
from actor.models import Actor, Member
from classify.models import Sector, Country
from ocsa_legacy.models import Capital
from actor.migrate.common import text_normalizer, ActorBase


class CapitalToActorMigration(ActorBase):
    errors = []

    def __init__(self):
        super().__init__()

        capitales = Capital.objects.all()
        self.current_capital = None

        self.countries = []

        self.empresariado = None
        try:
            self.empresariado = Sector.objects.get(name="Empresariado")
        except Sector.DoesNotExist:
            self.add_error("El sector Empresariado no existe")

        for capital in capitales:
            self.current_capital = capital
            self.countries = []
            self.need_review = None
            self.is_mexican = False
            try:
                self.migrate_to_actor(capital)
            except Exception as e:
                self.add_error(str(e))

    def add_error(self, message: str):
        self.errors.append([self.current_capital, message])

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

        self.get_countries()

        nombre = capital.nombre
        matriz = capital.matriz
        filial = capital.filial
        std_nombre = text_normalizer(nombre)
        std_matriz = text_normalizer(matriz)
        std_filial = text_normalizer(filial)

        real_count = (bool(nombre) + bool(matriz) + bool(filial))

        final_name = None

        warning_change = ("YEEKO: La filial se interpretó como la matriz, "
                          "pero no necesariamenete es correcto")

        mention = self.get_mention(capital)
        if real_count == 0:
            self.add_error("Ningún nombre de empresa se encontró")
            mention.add_comment("YEEKO: Hay al menos un capital sin nombre")
            mention.note.status_register_id = "need_new_checking"
            mention.note.add_comment(
                "YEEKO: En alguna mención existe un capital sin nombre")
            return
        elif real_count == 1:
            final_name = nombre or matriz or filial
            # std_final_name = std_nombre or std_matriz or std_filial
        else:
            if nombre and std_nombre == std_filial:
                filial = None

            if matriz and std_matriz == std_filial:
                filial = None

            if nombre and std_nombre == std_matriz:
                matriz = None

            if nombre and not matriz and filial:
                if std_nombre != std_filial:
                    self.need_review = warning_change
                    matriz = filial
                    std_matriz = std_filial
                filial = None

            real_count = (bool(nombre) + bool(matriz) + bool(filial))
            if real_count == 1:
                final_name = nombre or matriz or filial

        actor = None
        matriz_actor = None
        filial_actor = None

        created_actor = False
        created_matriz = False
        created_filial = False

        if final_name:
            actor, created_actor = Actor.objects.get_or_create(name=final_name)
        elif real_count > 1:
            if nombre:
                actor, created_actor = self.get_actor(nombre, std_nombre)
            if matriz:
                matriz_actor, created_matriz = self.get_actor(
                    matriz, std_matriz)
            if filial:
                filial_actor, created_filial = self.get_actor(
                    filial, std_filial)

        if actor:
            if matriz_actor:
                self.add_parent(actor, matriz_actor)
            actor = self.save_capital_features(actor, mention)
            self.add_participant(actor, mention, ["Capital"])
            self.register_origin(
                actor, capital.pk, "Capital", created_actor, field="nombre")
        if matriz_actor:
            if actor and matriz_actor.is_only_related is False:
                matriz_actor.is_only_related = True
            matriz_actor = self.save_capital_features(matriz_actor)
            self.register_origin(
                matriz_actor, capital.pk, "Capital", created_matriz, field="matriz")

        if filial_actor:
            if matriz_actor:
                self.add_parent(filial_actor, matriz_actor)
            elif actor:
                self.add_parent(filial_actor, actor)
            self.add_participant(filial_actor, mention, ["Capital"])
            filial_actor.is_only_related = True
            filial_actor = self.save_capital_features(filial_actor)
            self.register_origin(
                filial_actor, capital.pk, "Capital", created_filial, field="filial")

        main_actor = actor or matriz_actor or filial_actor
        if not main_actor:
            self.errors.append([capital, "No actor created"])
            return
        main_actor.is_only_related = False
        main_actor.capital_extension = self.get_capital_extension(  # type: ignore
            main_actor, capital)

        self.append_directors(main_actor)

        main_actor.save()

    def get_countries(self):
        names = getattr(self.current_capital, "nacionalidad", None)
        if not names:
            return
        mexican_countries = ["México", "Mexicana"]
        names = names.replace("/", ";")
        names = names.replace("-", ";")
        names = names.replace(" y ", ";")
        countries = names.split(";")
        for name in countries:
            name = name.strip()
            if name in mexican_countries:
                self.is_mexican = True
            country_obj, _ = Country.objects.get_or_create(name=name)
            self.countries.append(country_obj)

    def get_capital_extension(self, actor: Actor, capital: Capital):
        capital_extension = actor.capital_extension or {}
        fields = ["inversionistas", "is_cotiza_bolsa"]
        for field in fields:
            saved_value = capital_extension.get(field, [])
            value = getattr(capital, field)
            if value is not None:
                saved_value.append(value)
                capital_extension[field] = saved_value
        return capital_extension

    def save_capital_features(self, actor: Actor,  mention=None) -> Actor:
        if self.need_review:
            actor.status_validation_id = "need_review"  # type: ignore
            actor.add_comment(self.need_review)

        is_private = not getattr(self.current_capital,
                                 "is_capital_publico", None)
        if not is_private:
            sector_name = "Empresa estatal"
        elif self.is_mexican:
            sector_name = "Empresa privada nacional"
        elif self.countries:
            sector_name = "Empresa privada extranjera"
            for country in self.countries:
                actor.countries.add(country)
        else:
            sector_name = "Empresa privada"

        try:
            sector_obj = Sector.objects.get(name=sector_name)
        except Sector.DoesNotExist:
            self.add_error(f"El sector {sector_name} no existe")
            actor.status_validation_id = "need_review"  # type: ignore
            actor.add_comment(f"YEEKO: El sector {sector_name} no existe")
            return actor

        if not actor.sector:
            actor.sector = sector_obj
        elif actor.sector.name != sector_name:
            if sector_name == "Empresa privada":
                pass
            elif actor.sector.name == "Empresa privada":
                actor.sector = sector_obj
            else:
                comment = (
                    f"YEEKO: El actor tiene registrado más de un tipo de "
                    f"capital: {actor.sector.name} y {sector_obj.name}")
                sector_obj, _ = Sector.objects.get_or_create(
                    name="Contradictorio",
                    sector_group=self.get_sector_group_default(),
                    status_validation_id="need_review")
                actor.sector = sector_obj
                actor.status_validation_id = "need_review"  # type: ignore
                actor.add_comment(comment)
        actor.save()
        return actor

    def append_directors(self, actor: Actor):
        directors = getattr(self.current_capital, "directores", None) or ""
        capital_pk = getattr(self.current_capital, "pk", None) or ""
        directors = directors.replace(" y ", ";").split(";")
        for director in directors:
            director = director.strip()
            if not director:
                continue
            actor_director, created = Actor.objects.get_or_create(
                name=director, sector=self.empresariado)
            if created or actor_director.is_only_related is None:
                actor_director.is_only_related = False
            actor_director.save()
            self.register_origin(
                actor_director, capital_pk, "Capital", created,
                field="directores")
            Member.objects.get_or_create(
                actor_individual=actor_director, actor_collective=actor,
                membership_type="director")
