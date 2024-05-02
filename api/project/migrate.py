from typing import Dict, Optional
from ocsa_legacy.models import CSA, Proyecto, TipoDespliegueCapital, TipoMegaproyecto
from project.models import Conflict, DeploymentCapitalType, MegaprojectType, Project, Scale


class ProyectoToProject:
    errors: list = []
    conflicts: Dict[str, Conflict] = {}
    mega_project_types: Dict[str, MegaprojectType] = {}
    deployment_capital_types: Dict[str, DeploymentCapitalType] = {}
    scales: Dict[str, Scale] = {}

    def __init__(self):
        self.set_conflicts()
        self.set_deployment_capital_types_exclude_mix()
        self.set_deployment_capital_types_filter_mix()
        self.set_megaproject_types()

        proyectos = Proyecto.objects.all().order_by("id")
        print(f"Processing {proyectos.count()} proyectos")
        for proyecto in proyectos:
            print(f"Processing proyecto {proyecto.pk}: {proyecto.nombre}")
            try:
                self.migrate_proyecto(proyecto)
            except Exception as e:
                self.errors.append([proyecto, e])

    def set_conflicts(self):
        csa_query = CSA.objects.all()
        for csa in csa_query:
            if not csa.nombre:
                continue
            conflict, _ = Conflict.objects.get_or_create(name=csa.nombre)
            self.conflicts[csa.nombre] = conflict

    def get_conflict(self, csa_name: str):
        return self.conflicts[csa_name]

    def set_deployment_capital_types_exclude_mix(self):
        tipo_despliegue_capital_query = TipoDespliegueCapital.objects\
            .exclude(nombre__istartswith='mixto')

        for tipo_despliegue_capital in tipo_despliegue_capital_query:
            self.create_deployment_capital_type(tipo_despliegue_capital)

    def set_deployment_capital_types_filter_mix(self, mixto=False):
        tipo_despliegue_capital_query = TipoDespliegueCapital.objects\
            .filter(nombre__istartswith='mixto')

        for tipo_despliegue_capital in tipo_despliegue_capital_query:
            if not tipo_despliegue_capital.nombre:
                continue

            names = tipo_despliegue_capital.nombre[6:].split('/')
            for name in names:
                self.create_deployment_capital_type(
                    tipo_despliegue_capital, name.strip())

    def create_deployment_capital_type(
            self, tipo_despliegue_capital: TipoDespliegueCapital,
            nombre: Optional[str] = None
    ):
        nombre = nombre or tipo_despliegue_capital.nombre
        if not nombre:
            return
        descripcion = tipo_despliegue_capital.descripcion
        color = tipo_despliegue_capital.color

        deployment_capital_type, created = DeploymentCapitalType.objects\
            .get_or_create(name=nombre)
        save = False

        if descripcion and created:
            deployment_capital_type.description = descripcion
            save = True

        if color and created:
            deployment_capital_type.color = color
            save = True

        if save:
            deployment_capital_type.save()

        self.deployment_capital_types[nombre] = deployment_capital_type

    def get_deployment_capital_type(self, tipo_despliegue_capital_nombre):
        return self.deployment_capital_types[tipo_despliegue_capital_nombre]

    def set_megaproject_types(self):
        # se tiene que separa los megaproyectos convinados?
        # ejem: Termoeléctrica / Gasoducto / Acueducto
        tipos_megaproyecto = TipoMegaproyecto.objects.all()
        for tipo_megaproyecto in tipos_megaproyecto:
            if not tipo_megaproyecto.nombre:
                continue
            megaproject_type, _ = MegaprojectType.objects.get_or_create(
                name=tipo_megaproyecto.nombre)

            if tipo_megaproyecto.descripcion:
                megaproject_type.description = tipo_megaproyecto.descripcion
                megaproject_type.save()

            self.mega_project_types[tipo_megaproyecto.nombre] = megaproject_type

    def get_megaproject_type(
            self, tipo_megaproyecto_nombre,
            tipo_despliegue_capital: Optional[TipoDespliegueCapital] = None):
        megaproject_type = self.mega_project_types[tipo_megaproyecto_nombre]

        if not tipo_despliegue_capital:
            return megaproject_type
        tdc_name = tipo_despliegue_capital.nombre
        if tdc_name and tdc_name.lower().startswith('mixto'):
            names = tdc_name[6:].split('/')
            for name in names:
                self.add_deployment_capital_type(
                    megaproject_type, name.strip())
        elif tdc_name:
            self.add_deployment_capital_type(
                megaproject_type, tdc_name)

        if megaproject_type.deployment_capital_types.count() > 1:
            megaproject_type.has_many_dct = True
            megaproject_type.save()

        return megaproject_type

    def add_deployment_capital_type(
            self, megaproject_type: MegaprojectType,
            tipo_despliegue_capital_name: str):
        deployment_capital_type = self.get_deployment_capital_type(
            tipo_despliegue_capital_name.strip())
        megaproject_type.deployment_capital_types.add(deployment_capital_type)

    def get_scale(self, escala: str):
        if escala in self.scales:
            return self.scales[escala]
        scale, _ = Scale.objects.get_or_create(name=escala)
        self.scales[escala] = scale
        return scale

    def get_project(self, proyecto: Proyecto) -> Project:
        project = Project.objects.filter(proyecto_id_ref=proyecto.pk).first()
        if project:
            # print(
            #     f"Project {proyecto} from proyecto {proyecto} already exists")
            return project

        description = None
        if proyecto.especificaciones != "SD":
            description = proyecto.especificaciones

        conflict = None
        if proyecto.csa and proyecto.csa.nombre:
            conflict = self.get_conflict(proyecto.csa.nombre)

        megaproject_type = self.get_megaproject_type(
            proyecto.tipo_megaproyecto.nombre,
            proyecto.tipo_despliegue_capital) if proyecto.tipo_megaproyecto else None

        scale = self.get_scale(proyecto.escala) if proyecto.escala else None

        project = Project.objects.create(
            legacy_id_mp=proyecto.id_mp,
            official_name=proyecto.nombre,
            scale=scale,
            megaproject_type=megaproject_type,
            description=description,
            conflict=conflict,

            proyecto_id_ref=proyecto.pk,
        )
        # print(f"Project {proyecto} from proyecto {proyecto} created")
        return project

    def migrate_proyecto(self, proyecto: Proyecto):
        project_a = self.get_project(proyecto)

        if not proyecto.proyecto_vinculado:
            return
        if project_a.parent_project:
            # print(f"Already has parent")
            return

        project_b = self.get_project(proyecto.proyecto_vinculado)

        if project_b.parent_project == project_a:
            # CASO 2, doble relación
            # cluster artificial anque sea cluster?
            pass
        elif proyecto.proyecto_vinculado.escala == "Cluster":
            project_a.parent_project = project_b  # type: ignore
            project_a.save()
            return

        project_c, _ = Project.objects.get_or_create(
            official_name=f"CLUSTER CREADO desde {project_b.official_name} - {project_b.pk}",
            scale=self.get_scale("Cluster artificial"),
        )

        project_a.parent_project = project_c  # type: ignore
        project_a.save()
        project_b.parent_project = project_c  # type: ignore
        project_b.save()
