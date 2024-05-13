from django.db import models

from utils.obj_str import nombre_or_pk


class CustomModel(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self._meta.fields:
            field.type = field.__class__.__name__
            if field.type not in ['CharField', 'TextField']:
                continue
            value = getattr(self, field.name)
            if value == 'SD' and field.null:
                setattr(self, field.name, None)

    class Meta:
        abstract = True


# Create your models here.
# ======================== Space Time ========================================

# CREATE TABLE ocs.ubicaciones (
#     id integer NOT NULL,
#     tipo_ubicacion ocs.tipo_ubicacion_e DEFAULT 'punto'::ocs.tipo_ubicacion_e,
#     estado text,
#     municipio text,
#     localidad text,
#     especificaciones text,
#     sitio text,
#     latitud double precision,
#     longitud double precision,
#     geom text
# );


class Ubicacion(CustomModel):
    tipo_ubicacion = models.CharField(
        max_length=100, default='punto', blank=True, null=True)
    estado = models.TextField(blank=True, null=True)
    municipio = models.TextField(blank=True, null=True)
    localidad = models.TextField(blank=True, null=True)
    especificaciones = models.TextField(blank=True, null=True)
    sitio = models.TextField(blank=True, null=True)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)
    geom = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.sitio or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        db_table = 'ubicaciones'

# CREATE TABLE ocs.cat_temporalidad (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class CatTemporalidad(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Cat Temporalidad'
        verbose_name_plural = 'Cat Temporalidades'
        db_table = 'cat_temporalidad'


# CREATE TABLE ocs.temporalidad (
#     id integer NOT NULL,
#     fecha date,
#     intervalo interval,
#     day_undefined boolean DEFAULT false,
#     month_undefined boolean DEFAULT false,
#     cat_temporalidad_id integer  --ForeignKey
# );

class Temporalidad(CustomModel):
    fecha = models.DateField(blank=True, null=True)
    intervalo = models.DurationField(blank=True, null=True)
    day_undefined = models.BooleanField(default=False, blank=True, null=True)
    month_undefined = models.BooleanField(default=False, blank=True, null=True)
    cat_temporalidad = models.ForeignKey(
        CatTemporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.cat_temporalidad, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Temporalidad'
        verbose_name_plural = 'Temporalidades'
        db_table = 'temporalidad'

# ======================== project: ========================================
# --------------------- Conflictos SocioAmbientales ---------------------------

# CREATE TABLE ocs.csa (
#     id integer NOT NULL,
#     nombre text
# );


class CSA(CustomModel):
    nombre = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'CSA'
        verbose_name_plural = 'CSAs'
        db_table = 'csa'

# ------------------------------ Proyectos --------------------------------

# -- Clasificaciones de proyecto


# CREATE TABLE ocs.cat_tipo_despliegue_capital (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text,
#     icono text,
#     color text
# );
class TipoDespliegueCapital(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    # RICK: Pendiente de migrar porque está raro.
    icono = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'
        db_table = 'cat_tipo_despliegue_capital'


# CREATE TABLE ocs.cat_tipo_megaproyecto (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoMegaproyecto(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Tipo Megaproyecto'
        verbose_name_plural = 'Tipos Megaproyecto'
        db_table = 'cat_tipo_megaproyecto'

# CREATE TABLE ocs.cat_estatus_proyecto (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class EstatusProyecto(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Estatus Proyecto'
        verbose_name_plural = 'Estatus Proyectos'
        db_table = 'cat_estatus_proyecto'


# CREATE TABLE ocs.proyectos (
#     id integer NOT NULL,
#     id_mp integer,
#     nombre text,
#     escala text,
#     tipo_despliegue_capital_id integer,  --ForeignKey
#     tipo_megaproyecto_id integer,  --ForeignKey
#     especificaciones text,
#     csa_id integer,  --ForeignKey
#     proyecto_vinculado_id integer,  --ForeignKey
#     old_ubis bigint
# );
class Proyecto(CustomModel):
    id_mp = models.IntegerField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    escala = models.TextField(blank=True, null=True)
    tipo_despliegue_capital = models.ForeignKey(
        TipoDespliegueCapital, on_delete=models.CASCADE, blank=True, null=True)
    tipo_megaproyecto = models.ForeignKey(
        TipoMegaproyecto, on_delete=models.CASCADE, blank=True, null=True)
    especificaciones = models.TextField(blank=True, null=True)
    csa = models.ForeignKey(
        CSA, on_delete=models.CASCADE, blank=True, null=True)
    proyecto_vinculado = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True)
    # COLUMNA VACÍA
    old_ubis = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        db_table = 'proyectos'

# --ubicaciones

# CREATE TABLE ocs.proyectos_to_ubicaciones (
#     id bigint NOT NULL,
#     proyecto_id bigint,
#     ubicacion_id bigint
# );


class ProyectoToUbicacion(CustomModel):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, blank=True, null=True)
    ubicacion = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.proyecto, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Proyecto a Ubicación'
        verbose_name_plural = 'Proyectos a Ubicaciones'
        db_table = 'proyectos_to_ubicaciones'


# ======================== Source ========================================
# CREATE TABLE ocs.notas (
#     id integer NOT NULL,
#     id_nota integer,
#     titulo text,
#     autor text,
#     nombre_medio text,
#     pagina_medio text,
#     vinculo text,
#     fecha date,
#     fecha_captura date
# );

class Nota(CustomModel):
    id_nota = models.IntegerField(blank=True, null=True)
    titulo = models.TextField(blank=True, null=True)
    autor = models.TextField(blank=True, null=True)
    nombre_medio = models.TextField(blank=True, null=True)
    pagina_medio = models.TextField(blank=True, null=True)
    vinculo = models.TextField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    fecha_captura = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.titulo or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        db_table = 'notas'


# CREATE TABLE ocs.registro_notas (
#     id integer NOT NULL,
#     owner text,
#     datum jsonb,
#     status ocs.draft_status DEFAULT 'inprogress'::ocs.draft_status,
#     last_edit timestamp with time zone DEFAULT CURRENT_TIMESTAMP
# );


# ALTER TABLE ocs.registro_notas ENABLE ROW LEVEL SECURITY;

class RegistroNotas(CustomModel):
    owner = models.TextField(blank=True, null=True)
    datum = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=100, default='inprogress', blank=True, null=True)
    last_edit = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.owner or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Registro Nota'
        verbose_name_plural = 'Registros Notas'
        db_table = 'registro_notas'


# CREATE TABLE ocs.estatus_proyectos (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     estatus_id integer,  --ForeignKey
#     temporalidad_id integer  --ForeignKey
# );

class EstatusProyectos(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    estatus = models.ForeignKey(
        EstatusProyecto, on_delete=models.CASCADE, blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nota

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Estatus Proyecto'
        verbose_name_plural = 'Estatus Proyectos'
        db_table = 'estatus_proyectos'


# ======================== actor 1: ========================================
# --------------------- Capitalistas (actores) -------------------------------

# CREATE TABLE ocs.capital (
#     id integer NOT NULL,
#     proyecto_id integer NOT NULL,  --ForeignKey
#     nota_id integer,  --ForeignKey
#     nombre text,
#     matriz text,
#     filial text,
#     directores text,
#     inversionistas text,
#     nacionalidad text,
#     is_capital_publico boolean,
#     is_cotiza_bolsa boolean,
#     interes text,
#     is_activo boolean
# );

class Capital(CustomModel):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    # Al final del script, utilizando Capital.matriz:
    # Si no existe, crear un nuevo Actor solo con ese nombre,
    # y ponerle is_only_related = True
    # Por el contrario, con el campo de Capital.filial se creará un nuevo actor
    # cuyo parent_actor será el registro actual
    matriz = models.TextField(blank=True, null=True)
    filial = models.TextField(blank=True, null=True)
    # NUEVO 2: Hay que separar a los directores (por punto y coma y "y")
    # Cada uno de los directores tendrá su parent_actor a main_actor
    # y su Sector será "Empresarios" y el SectorGroup será "Individuales"
    directores = models.TextField(blank=True, null=True)
    # los 2 siguientes campos inversionistas, is_cotiza_bolsa,
    # ayudaran a construir el campo "capital_extension"
    inversionistas = models.TextField(blank=True, null=True)
    nacionalidad = models.TextField(blank=True, null=True)
    is_capital_publico = models.BooleanField(blank=True, null=True)
    is_cotiza_bolsa = models.BooleanField(blank=True, null=True)
    interes = models.TextField(blank=True, null=True)
    # CAMPO VACÍO
    is_activo = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Capital'
        verbose_name_plural = 'Capitales'
        db_table = 'capital'


# ------------------ Instituciones del estado (actores) ------------------------


# CREATE TABLE ocs.estado (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     instituciones_a_favor_proyecto text,
#     instituciones_mediadoras text,
#     instituciones_atienden_reclamos text,
#     temporalidad_id integer  --ForeignKey
# );

class Estado(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    # participant_type = Estado
    instituciones_a_favor_proyecto = models.TextField(blank=True, null=True)
    # participant_type = Mediador
    instituciones_mediadoras = models.TextField(blank=True, null=True)
    # participant_type = Atención a reclamos
    instituciones_atienden_reclamos = models.TextField(blank=True, null=True)
    # RICK Y LUCIAN: Aún no le encuentro sentido a este campo
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.proyecto or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        db_table = 'estado'


# --------------------- Opositores (actores) --------------------------------

# -- cats

# CREATE TABLE ocs.cat_forma_organizacion (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


# Esto alimentará a Sector: todos tendrán el sector con nombre "Varios",
# y con is_collective = True
class FormaOrganizacion(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Forma Organización'
        verbose_name_plural = 'Formas Organización'
        db_table = 'cat_forma_organizacion'


# CREATE TABLE ocs.cat_mujer (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class Mujer(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Mujer'
        verbose_name_plural = 'Mujeres'
        db_table = 'cat_mujer'


# -- opositores

# CREATE TABLE ocs.opositores (
#     id integer NOT NULL,
#     nombre text,
#     forma_organizacion_id integer,  --ForeignKey
#     is_indigena boolean,
#     pueblo_indigena text,
#     is_campesino_or_comunero_or_ejidatario boolean,
#     mujer_id integer,  --ForeignKey
#     is_trabajador_empresa boolean,
#     otros_opositores text,
#     is_habitante_zona boolean
# );

class Opositores(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    forma_organizacion = models.ForeignKey(
        FormaOrganizacion, on_delete=models.CASCADE, blank=True, null=True)
    # is_women_special => Mujer
    # Esto se construye a partir de Opositor.mujer,
    # cuando Opositor.mujer tiene valor y su id es mayor o igual a 2;
    # RICK: Aún no sé bien qué vamos a hacer con este campo
    mujer = models.ForeignKey(
        Mujer, on_delete=models.CASCADE, blank=True, null=True)
    # is_farmer => Campesino
    is_campesino_or_comunero_or_ejidatario = models.BooleanField(
        blank=True, null=True)
    # is_worker => Trabajador
    is_trabajador_empresa = models.BooleanField(blank=True, null=True)
    # is_habitant => Habitante
    is_habitante_zona = models.BooleanField(blank=True, null=True)
    # is_indigena => Indígena
    is_indigena = models.BooleanField(blank=True, null=True)
    # Va a Actor.indigenous_group, también agregar Belong "is_indigena"
    pueblo_indigena = models.TextField(blank=True, null=True)
    otros_opositores = models.TextField(blank=True, null=True)
    # RICK: Falta decidir el comportamiento de este campo
    # ubicaciones

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Opositor'
        verbose_name_plural = 'Opositores'
        db_table = 'opositores'


# -- relacionales

# CREATE TABLE ocs.opositores_to_proyecto (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     proyecto_id integer  --ForeignKey
# );

class OpositorToProyecto(CustomModel):
    opositor = models.ForeignKey(
        Opositores, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.opositor, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Opositor a Proyecto'
        verbose_name_plural = 'Opositores a Proyectos'
        db_table = 'opositores_to_proyecto'

# CREATE TABLE ocs.opositores_to_notas (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     nota_id integer  --ForeignKey
# );


class OpositorToNotas(CustomModel):
    opositor = models.ForeignKey(
        Opositores, on_delete=models.CASCADE)
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.opositor, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Opositor a Nota'
        verbose_name_plural = 'Opositores a Notas'
        db_table = 'opositores_to_notas'


# --ubicaciones

# CREATE TABLE ocs.opositores_to_ubicaciones (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

class OpositorToUbicaciones(CustomModel):
    opositor = models.ForeignKey(
        Opositores, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.opositor, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Opositor a Ubicación'
        verbose_name_plural = 'Opositores a Ubicaciones'
        db_table = 'opositores_to_ubicaciones'

# -- Intereses

# CREATE TABLE ocs.intereses_opositores (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     opositor_id integer,  --ForeignKey
#     interes text
# );


class InteresesOpositores(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    opositor = models.ForeignKey(
        Opositores, on_delete=models.CASCADE, blank=True, null=True)
    interes = models.TextField(blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.opositor, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Interés Opositor'
        verbose_name_plural = 'Intereses Opositores'
        db_table = 'intereses_opositores'


# --------------------- Poblaciones (actores) --------------------------------

# -- Cats

# CREATE TABLE ocs.cat_poblacion_afectada (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class CatPoblacionAfectada(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Cat Población Afectada'
        verbose_name_plural = 'Cat Poblaciones Afectadas'
        db_table = 'cat_poblacion_afectada'


# CREATE TABLE ocs.cat_subpoblacion_afectada (
#     id integer NOT NULL,
#     id_subpoblacion_af integer,
#     nombre text,
#     descripcion text
# );

class CatSubpoblacionAfectada(CustomModel):
    # CAMPO VACÍO
    id_subpoblacion_af = models.IntegerField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Cat Subpoblación Afectada'
        verbose_name_plural = 'Cat Subpoblaciones Afectadas'
        db_table = 'cat_subpoblacion_afectada'

# -- Poblaciones

# CREATE TABLE ocs.poblaciones_afectadas (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     poblacion_afectada_id integer,  --ForeignKey
#     subpoblacion_afectada_id integer,  --ForeignKey
#     descripcion text,
#     interes text,
#     ubicacion_id integer  --ForeignKey
# );


# Agregar belong "is_affected"
# Todos los de la tabla PopulacionesAfectadas tendrán este campo
class PoblacionAfectada(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    # BELONGS:
    # is_habitant => Habitante
    # PoblacionesAfectadas: name == "Pobladores" or name == "Vecinos"
    # is_worker => Trabajador
    # PoblacionesAfectadas: name == "Trabajadores de la empresa"
    # is_indigena => Indígena
    # PoblacionesAfectadas: name == "Indígena"
    # is_farmer => Campesino
    # PoblacionesAfectadas: name == "Campesino/Comunero/Ejidatario"
    poblacion_afectada = models.ForeignKey(
        CatPoblacionAfectada, on_delete=models.CASCADE, blank=True, null=True)
    # Actor. indigenous_group
    # cuando el id > 4 ; también agregar su belong de "is_indigena"
    subpoblacion_afectada = models.ForeignKey(
        CatSubpoblacionAfectada, on_delete=models.CASCADE, blank=True, null=True)
    # Este campo ayuda a construir 'nombre'. Hay varios registros
    # que tienen comillas, están raros, parecen como no terminados
    descripcion = models.TextField(blank=True, null=True)
    interes = models.TextField(blank=True, null=True)
    # RICK: Falta decidir el comportamiento de este campo
    ubicacion = models.ForeignKey(
        Ubicacion, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.poblacion_afectada, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Población Afectada'
        verbose_name_plural = 'Poblaciones Afectadas'
        db_table = 'poblaciones_afectadas'


# -- intereses

# CREATE TABLE ocs.intereses_poblacion (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     poblacion_afectada_id integer,  --ForeignKey
#     interes text
# );

# TABLA VACÍA
class InteresesPoblacion(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    # RICK Y LUCIAN: Este campo parece repetido, similar a nota y proyecto
    # ¿Qué podríamos hacer para mantener la congruencia?
    poblacion_afectada = models.ForeignKey(
        PoblacionAfectada, on_delete=models.CASCADE, blank=True, null=True)
    interes = models.TextField(blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.poblacion_afectada, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Interés Población'
        verbose_name_plural = 'Intereses Poblaciones'
        db_table = 'intereses_poblacion'


# CREATE TABLE ocs.grupos_apoyo (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_grupo_apoyo text,
#     nombre text,
#     interes text
# );

class GruposApoyo(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    # Los GruposApoyo que tengan "Empresa" tendrán participante_type = "Partidario"
    # Los GruposApoyo que tengan "Opositor" u "Opositores" tendrán
    # participante_type = "Acompañante solidario"
    tipo_grupo_apoyo = models.TextField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    interes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Grupo Apoyo'
        verbose_name_plural = 'Grupos Apoyo'
        db_table = 'grupos_apoyo'


# --------------------- impact --------------------------------

# CREATE TABLE ocs.cat_tipo_afectaciones_ecologicas (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoAfectacionEcologica(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Tipo Afectación Ecológica'
        verbose_name_plural = 'Tipos Afectaciones Ecológicas'
        db_table = 'cat_tipo_afectaciones_ecologicas'

# CREATE TABLE ocs.afectaciones_ecologicas (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_ae_id integer,  --ForeignKey
#     descripcion_ae text,
#     temporalidad_id integer  --ForeignKey
# );


class AfectacionEcologica(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_ae = models.ForeignKey(
        TipoAfectacionEcologica, on_delete=models.CASCADE, blank=True, null=True)
    descripcion_ae = models.TextField(blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.tipo_ae, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Afectación Ecológica'
        verbose_name_plural = 'Afectaciones Ecológicas'
        db_table = 'afectaciones_ecologicas'

# --ubicaciones

# CREATE TABLE ocs.ae_to_ubicaciones (
#     id integer NOT NULL,
#     afectacion_ecologica_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );


class AfectacionEcologicaToUbicacion(CustomModel):
    afectacion_ecologica = models.ForeignKey(
        AfectacionEcologica, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.afectacion_ecologica.proyecto, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Afectación Ecológica a Ubicación'
        verbose_name_plural = 'Afectaciones Ecológicas a Ubicaciones'
        db_table = 'ae_to_ubicaciones'


# CREATE TABLE ocs.cat_tipo_afectaciones_sociales (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


class TipoAfectacionSocial(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Tipo Afectación Social'
        verbose_name_plural = 'Tipos Afectaciones Sociales'
        db_table = 'cat_tipo_afectaciones_sociales'


# CREATE TABLE ocs.afectaciones_sociales (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_as_id integer,  --ForeignKey
#     descripcion_as text,
#     temporalidad_id integer  --ForeignKey
# );

class AfectacionSocial(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_as = models.ForeignKey(
        TipoAfectacionSocial, on_delete=models.CASCADE, blank=True, null=True)
    descripcion_as = models.TextField(blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.tipo_as, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Afectación Social'
        verbose_name_plural = 'Afectaciones Sociales'
        db_table = 'afectaciones_sociales'

# # --ubicaciones

# CREATE TABLE ocs.as_to_ubicaciones (
#     id integer NOT NULL,
#     afectacion_social_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );


class AfectacionSocialToUbicacion(CustomModel):
    afectacion_social = models.ForeignKey(
        AfectacionSocial, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.afectacion_social.proyecto, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Afectación Social a Ubicación'
        verbose_name_plural = 'Afectaciones Sociales a Ubicaciones'
        db_table = 'as_to_ubicaciones'


# CREATE TABLE ocs.otros (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_propiedad text,
#     fortalecimiento_tejido_social text,
#     descripcion text
# );


class Otros(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    tipo_propiedad = models.TextField(blank=True, null=True)
    fortalecimiento_tejido_social = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tipo_propiedad or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Otro'
        verbose_name_plural = 'Otros'
        db_table = 'otros'


# ======================== Evento ========================================
# # --------------------- Violencias (eventos) --------------------------------

# CREATE TABLE ocs.cat_hechos_violencia (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

# Esto se va a EventType con el EventGroup =
# (name='Violencia', model_origin='HechosViolencia')
class HechosViolencia(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Hecho Violencia'
        verbose_name_plural = 'Hechos Violencia'
        db_table = 'cat_hechos_violencia'


# CREATE TABLE ocs.cat_forma_hecho_violencia (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

# Esto se va a EventSubtype, el cual vamos a dejar por ahora sin relación
# directa con event_types, después, a través de la tabla Violencias vamos a
# hacer la relación entre las categorías.
# Si el valor de "nombre" es NE, ignorarlo por el momento, pero en Violencias
# sí se tomará en cuenta.
class FormaHechoViolencia(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Forma Hecho Violencia'
        verbose_name_plural = 'Formas Hecho Violencia'
        db_table = 'cat_forma_hecho_violencia'


# CREATE TABLE ocs.cat_condicion_mujer_victima (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class CondicionMujerVictima(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Condición Mujer Víctima'
        verbose_name_plural = 'Condiciones Mujer Víctima'
        db_table = 'cat_condicion_mujer_victima'

# CREATE TABLE ocs.cat_sector_social (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


# Esta tabla va a alimentar a la tabla "Sector" de actor. Si no está creado,
# crearlo con el sector_group.name = "Varios" y el campo is_collective = True,
# Excepto los siguientes nombres:
# "Trabajador de la empresa", "Otro (Abogado opositor)", "Periodista",
# "Abogado", "Activista", "Agente Federal", "Activista", "Defensor Ambiental",
# "Comerciante", "Defensor Ambiental", "Profesor", "Comunero",
# "Defensor del territorio", "Comunicador", "Profesora", "Alcalde"
class SectorSocial(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Sector Social'
        verbose_name_plural = 'Sectores Sociales'
        db_table = 'cat_sector_social'


# CREATE TABLE ocs.violencias (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     hecho_violencia_id integer,  --ForeignKey
#     forma_hecho_violencia_id integer,  --ForeignKey
#     temporalidad_id integer,  --ForeignKey
#     num_victimas text,
#     is_hombres boolean,
#     is_mujeres boolean,
#     condicion_mujeres_victimas integer,
#     sector_social_victima integer,
#     is_victima_dirigente boolean,
#     responsable_estatal_desc text,
#     responsable_no_estatal_desc text
# );

# ANTES DE COMENZAR:
# Crear los registros iniciales de EventRole (idéntico a lo que hicimos
# con init_participant_types (checar el modelo EventRole
# INTRODUCCIÓN:
# La Tabla violencias se guardará en la tabla Event, pero algunos datos se
# guardarán en la tabla Actor. cada combinación de hecho_violencia y
# forma_hecho_violencia generará un nuevo Event. Los actores involucrados
# (tabla Involved) se guardarán por cada uno de los actores involucrados,
# tanto víctimas (sector social) como victimarios (responsables estatales
# y no estatales).

class Violencia(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    # Con los dos siguientes campos vamos, además de guardar los valores que
    # correspondan (event_type y event_subtype, vamos a generar la relación
    # de EventSubtype con EventType, por cada vez que aparezca, muy
    # parecido a lo que ya hicimos con MegaprojectType y DeploymentCapitalType
    # NOTA: Si el valor de forma_hecho_violencia.nombre es NE, crear un nuevo
    # EventSubtype con el nombre f"No Especificado de {hecho_violencia.nombre}"
    hecho_violencia = models.ForeignKey(
        HechosViolencia, on_delete=models.CASCADE, blank=True, null=True)
    forma_hecho_violencia = models.ForeignKey(
        FormaHechoViolencia, on_delete=models.CASCADE, blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)
    # Con los 3 siguientes campos vamos a construir los campos de Involved:
    # number_men, number_women y number_mix, cuando el número es 1 o 2,
    # pues hay que ver cuál es el género de todas las víctimas o si tiene
    # is_mujeres e is_hombres activos, pues dividir.
    # Si son más de 2 víctimas y hay 1 solo sexo activo, pues asignar a ese
    # género, si no, asignar a number_mix
    num_victimas = models.TextField(blank=True, null=True)
    is_hombres = models.BooleanField(blank=True, null=True)
    is_mujeres = models.BooleanField(blank=True, null=True)

    # RICK: Campo pendiente de clasificar
    condicion_mujeres_victimas = models.ForeignKey(
        CondicionMujerVictima, on_delete=models.CASCADE, blank=True, null=True,
        db_column='condicion_mujeres_victimas')
    # Si hay valor en este campo, se creará un registro de Actor con el nombre
    # f"Víctima del sector {sector_social_victima.nombre} del proyecto
    # {project.name}". El event_role.name, para sus Involved, será "Víctima"
    # Esto tiene que ver con la tabla Sector, hay que vincular el sector
    # al actor que generemos
    # Si hay dos registros con los mismos valores, hay que agregarle al nombre
    # un número consecutivo, para que tengamos nombres únicos
    sector_social_victima = models.ForeignKey(
        SectorSocial, on_delete=models.CASCADE, blank=True, null=True,
        db_column='sector_social_victima')

    # NUEVO:
    # PREVIO: Agregar un belong con el key_name = "is_leader" y
    # name = "Dirigente"
    # SEGUNDO PASO: los actores generados hay que agregarles el Belong de is_leader
    is_victima_dirigente = models.BooleanField(blank=True, null=True)

    # Todas las reglas aplican para los 2 siguientes campos:
    # Se creará (si no existe) un registro de Actor
    # Se debe agregar el participan_type "Por definir (de violencias)",
    # El Sector.nombre de responsable_estatal_desc será "Responsable Estatal" y
    # su SectorGroup.name será "Varios"
    # (a menos que el registro ya exista y ya tenga un sector asociado,
    # en cuyo caso, no se debe modificar)
    # El Sector.nombre de responsable_no_estatal_desc será
    # "Responsable No Estatal" y aplicar las mismas reglas de arriba
    # El event_role.name, para sus Involved generados será "Responsable"

    # Separar los valores de este campo por punto y coma ";", existe una
    # lista de excepciones en el excel, para dichos casos, hay que cambiar
    # el nombre y agregarles el nombre del proyecto,:
    # f"{responsable_ESTATAL_O_NO_ESTATAL_desc} del proyecto {project.name}"
    # También hay que dejarlos
    # con el status_validation de "need_review" y con el comentario siguiente:
    # YEEKO: Se creó este nombre porque se identificó como nombre genérico,
    # sin embargo, debe mejorar su nombre.
    # Para los nombres de la lista del excel, hay que agregar al actor,
    # el Sector con el nombre tal como viene
    responsable_estatal_desc = models.TextField(blank=True, null=True)
    responsable_no_estatal_desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.hecho_violencia, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Violencia'
        verbose_name_plural = 'Violencias'
        db_table = 'violencias'


# CREATE TABLE ocs.violencias_to_opositores (
#     id integer NOT NULL,
#     violencia_id integer,  --ForeignKey
#     opositor_id integer  --ForeignKey
# );

class ViolenciaToOpositor(CustomModel):
    violencia = models.ForeignKey(
        Violencia, on_delete=models.CASCADE)
    opositor = models.ForeignKey(
        Opositores, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.violencia.proyecto, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Violencia a Opositor'
        verbose_name_plural = 'Violencias a Opositores'
        db_table = 'violencias_to_opositores'


# # --ubicaciones

# CREATE TABLE ocs.violencias_to_ubicaciones (
#     id integer NOT NULL,
#     violencia_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

class ViolenciaToUbicacion(CustomModel):
    violencia = models.ForeignKey(
        Violencia, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.violencia.proyecto, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Violencia a Ubicación'
        verbose_name_plural = 'Violencias a Ubicaciones'
        db_table = 'violencias_to_ubicaciones'

# # --------------------- Acciones colectivas (eventos) --------------------------------

# CREATE TABLE ocs.cat_forma_ac (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );


# Vamos a hacer exactamente lo mismo que con HechosViolencia y
# FormaHechoViolencia, pero con FormaAC y SubformaAC,
# se vana a ir a EventType y EventSubtype. La diferencia es que sí
# existe desde el modelo SubformaAC, una relación directa con FormaAC
# El EventGroup será name = "Acciones Colectivas" y el model_origin será
# "FormaAC"
class FormaAC(CustomModel):
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Forma Acción Colectiva'
        verbose_name_plural = 'Formas Acciones Colectivas'
        db_table = 'cat_forma_ac'


# CREATE TABLE ocs.cat_subforma_ac (
#     id integer NOT NULL,
#     id_forma_ac integer,
#     nombre text,
#     descripcion text
# );
class SubformaAC(CustomModel):
    id_forma_ac = models.IntegerField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre or str(self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Subforma Acción Colectiva'
        verbose_name_plural = 'Subformas Acciones Colectivas'
        db_table = 'cat_subforma_ac'

# CREATE TABLE ocs.acciones_colectivas (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     forma_ac_id integer,  --ForeignKey
#     subforma_ac_id integer,  --ForeignKey
#     temporalidad_id integer  --ForeignKey
# );


# cada registro de AccionesColectivas generará un nuevo Event, los

class AccionesColectivas(CustomModel):
    nota = models.ForeignKey(
        Nota, on_delete=models.CASCADE, blank=True, null=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE)
    forma_ac = models.ForeignKey(
        FormaAC, on_delete=models.CASCADE, blank=True, null=True)
    subforma_ac = models.ForeignKey(
        SubformaAC, on_delete=models.CASCADE, blank=True, null=True)
    temporalidad = models.ForeignKey(
        Temporalidad, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.forma_ac, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Acción Colectiva'
        verbose_name_plural = 'Acciones Colectivas'
        db_table = 'acciones_colectivas'


# # -- relacional a opositor (y acción colectiva)

# CREATE TABLE ocs.opositores_to_ac (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     ac_id integer  --ForeignKey
# );


# Esta tabla ayudará a construir los Involved de los eventos, en este caso
# el event_role será "Accionante".

class OpositoresToAC(CustomModel):
    opositor = models.ForeignKey(
        Opositores, on_delete=models.CASCADE, blank=True, null=True)
    accion_colectiva = models.ForeignKey(
        AccionesColectivas, on_delete=models.CASCADE, db_column='ac_id', blank=True, null=True)

    def __str__(self):
        return nombre_or_pk(self.opositor, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Opositor a Acción Colectiva'
        verbose_name_plural = 'Opositores a Acciones Colectivas'
        db_table = 'opositores_to_ac'

# # --ubicaciones

# CREATE TABLE ocs.ac_to_ubicaciones (
#     id integer NOT NULL,
#     accion_colectiva_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );


class AccionColectivaToUbicacion(CustomModel):
    accion_colectiva = models.ForeignKey(
        AccionesColectivas, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return nombre_or_pk(self.accion_colectiva.proyecto, self.pk)

    class Meta:
        managed = False
        app_label = 'ocsa_legacy'
        verbose_name = 'Acción Colectiva a Ubicación'
        verbose_name_plural = 'Acciones Colectivas a Ubicaciones'
        db_table = 'ac_to_ubicaciones'
