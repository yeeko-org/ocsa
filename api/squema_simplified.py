from django.db import models

# -- ======================== CATS GENERALES ================================


# --- formas de organización y población


# CREATE TABLE ocs.cat_sector_social (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class SectorSocial(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Sector Social'
        verbose_name_plural = 'Sectores Sociales'
        db_table = 'cat_sector_social'


# -- Otros cats:


# CREATE TABLE ocs.cat_condicion_mujer_victima (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class CondicionMujerVictima(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Condición Mujer Víctima'
        verbose_name_plural = 'Condiciones Mujer Víctima'
        db_table = 'cat_condicion_mujer_victima'


# ---------------- Extensión de temporalidad (Para varios) -----------------



# CREATE TABLE ocs.cat_temporalidad (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class Temporalidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Temporalidad'
        verbose_name_plural = 'Temporalidades'
        db_table = 'cat_temporalidad'


# CREATE TABLE ocs.temporalidad (
#     id integer NOT NULL,
#     fecha date,
#     intervalo interval,
#     day_undefined boolean DEFAULT false,
#     month_undefined boolean DEFAULT false,
#     cat_temporalidad_id integer  --ForeignKey
# );

class Temporalidad(models.Model):
    fecha = models.DateField()
    intervalo = models.DurationField()
    day_undefined = models.BooleanField(default=False)
    month_undefined = models.BooleanField(default=False)
    cat_temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.fecha
    
    class Meta:
        verbose_name = 'Temporalidad'
        verbose_name_plural = 'Temporalidades'
        db_table = 'temporalidad'



# --------------------- Ubicaciones (para varias)--------------------------------



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

class Ubicacion(models.Model):
    tipo_ubicacion = models.CharField(max_length=100, default='punto')
    estado = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    localidad = models.CharField(max_length=100)
    especificaciones = models.TextField()
    sitio = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()
    geom = models.TextField()

    def __str__(self):
        return self.sitio
    
    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
        db_table = 'ubicaciones'



# -- ========================= NOTAS   =============================


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

class Nota(models.Model):
    id_nota = models.IntegerField()
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    nombre_medio = models.CharField(max_length=100)
    pagina_medio = models.CharField(max_length=100)
    vinculo = models.CharField(max_length=100)
    fecha = models.DateField()
    fecha_captura = models.DateField()

    def __str__(self):
        return self.titulo
    
    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        db_table = 'notas'


# -- No entiendo muy bien los siguientes 2 comandos:


# CREATE TABLE ocs.registro_notas (
#     id integer NOT NULL,
#     owner text,
#     datum jsonb,
#     status ocs.draft_status DEFAULT 'inprogress'::ocs.draft_status,
#     last_edit timestamp with time zone DEFAULT CURRENT_TIMESTAMP
# );


# ALTER TABLE ocs.registro_notas ENABLE ROW LEVEL SECURITY;

class RegistroNotas(models.Model):
    owner = models.CharField(max_length=100)
    datum = models.JSONField()
    status = models.CharField(max_length=100, default='inprogress')
    last_edit = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner
    
    class Meta:
        verbose_name = 'Registro Nota'
        verbose_name_plural = 'Registros Notas'
        db_table = 'registro_notas'




# -- ===================== PROYECTOS Y CONFLICTOS  =============================


# --------------------- Conflictos SocioAmbientales ---------------------------


# CREATE TABLE ocs.csa (
#     id integer NOT NULL,
#     nombre text
# );

class CSA(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
    class Meta:
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
class TipoDespliegueCapital(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.CharField(max_length=100)
    color = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Tipo Despliegue Capital'
        verbose_name_plural = 'Tipos Despliegue Capital'
        db_table = 'cat_tipo_despliegue_capital'


# CREATE TABLE ocs.cat_tipo_megaproyecto (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoMegaproyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Tipo Megaproyecto'
        verbose_name_plural = 'Tipos Megaproyecto'
        db_table = 'cat_tipo_megaproyecto'

# CREATE TABLE ocs.cat_estatus_proyecto (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );
class EstatusProyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
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
class Proyecto(models.Model):
    id_mp = models.IntegerField()
    nombre = models.CharField(max_length=100)
    escala = models.CharField(max_length=100)
    tipo_despliegue_capital = models.ForeignKey(TipoDespliegueCapital, on_delete=models.CASCADE)
    tipo_megaproyecto = models.ForeignKey(TipoMegaproyecto, on_delete=models.CASCADE)
    especificaciones = models.TextField()
    csa = models.ForeignKey(CSA, on_delete=models.CASCADE)
    proyecto_vinculado = models.ForeignKey('self', on_delete=models.CASCADE)
    old_ubis = models.BigIntegerField()
    ubicaciones = models.ManyToManyField('Ubicacion', db_table='ocs.proyectos_to_ubicaciones')


    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        db_table = 'proyectos'


# CREATE TABLE ocs.estatus_proyectos (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     estatus_id integer,  --ForeignKey
#     temporalidad_id integer  --ForeignKey
# );
class EstatusProyectos(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    estatus = models.ForeignKey(EstatusProyecto, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.nota.titulo
    
    class Meta:
        verbose_name = 'Estatus Proyecto'
        verbose_name_plural = 'Estatus Proyectos'
        db_table = 'estatus_proyectos'

# --ubicaciones

# CREATE TABLE ocs.proyectos_to_ubicaciones (
#     id bigint NOT NULL,
#     proyecto_id bigint,
#     ubicacion_id bigint
# );

# class ProyectosToUbicaciones(models.Model):
#     proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
#     ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.proyecto.nombre
    
#     class Meta:
#         verbose_name = 'Proyecto a Ubicación'
#         verbose_name_plural = 'Proyectos a Ubicaciones'
#         db_table = 'proyectos_to_ubicaciones'



# -- ======================== ACTORES (VARIOS) ================================


# --------------------- Capitalistas (actores) --------------------------------



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

class Capital(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    matriz = models.TextField()
    filial = models.TextField()
    directores = models.TextField()
    inversionistas = models.TextField()
    nacionalidad = models.CharField(max_length=100)
    is_capital_publico = models.BooleanField()
    is_cotiza_bolsa = models.BooleanField()
    interes = models.TextField()
    is_activo = models.BooleanField()

    def __str__(self):
        return self.nombre
    
    class Meta:
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

class Estado(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    instituciones_a_favor_proyecto = models.TextField()
    instituciones_mediadoras = models.TextField()
    instituciones_atienden_reclamos = models.TextField()
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.proyecto.nombre
    
    class Meta:
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

class FormaOrganizacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Forma Organización'
        verbose_name_plural = 'Formas Organización'
        db_table = 'cat_forma_organizacion'


# CREATE TABLE ocs.cat_mujer (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class Mujer(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
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

class Opositor(models.Model):
    nombre = models.CharField(max_length=100)
    forma_organizacion = models.ForeignKey(FormaOrganizacion, on_delete=models.CASCADE)
    is_indigena = models.BooleanField()
    pueblo_indigena = models.CharField(max_length=100)
    is_campesino_or_comunero_or_ejidatario = models.BooleanField()
    mujer = models.ForeignKey(Mujer, on_delete=models.CASCADE)
    is_trabajador_empresa = models.BooleanField()
    otros_opositores = models.TextField()
    is_habitante_zona = models.BooleanField()

    proyectos = models.ManyToManyField(Proyecto, db_table='ocs.opositores_to_proyecto')
    notas = models.ManyToManyField(Nota, db_table='ocs.opositores_to_notas')
    ubicaciones = models.ManyToManyField(Ubicacion, db_table='ocs.opositores_to_ubicaciones')

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Opositor'
        verbose_name_plural = 'Opositores'
        db_table = 'opositores'


# -- relacionales

# CREATE TABLE ocs.opositores_to_proyecto (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     proyecto_id integer  --ForeignKey
# );

# CREATE TABLE ocs.opositores_to_notas (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     nota_id integer  --ForeignKey
# );


# --ubicaciones

# CREATE TABLE ocs.opositores_to_ubicaciones (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

# -- Intereses

# CREATE TABLE ocs.intereses_opositores (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     opositor_id integer,  --ForeignKey
#     interes text
# );

class InteresesOpositores(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    opositor = models.ForeignKey(Opositor, on_delete=models.CASCADE)
    interes = models.TextField()

    def __str__(self):
        return self.opositor.nombre
    
    class Meta:
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

class PoblacionAfectada(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Población Afectada'
        verbose_name_plural = 'Poblaciones Afectadas'
        db_table = 'cat_poblacion_afectada'


# CREATE TABLE ocs.cat_subpoblacion_afectada (
#     id integer NOT NULL,
#     id_subpoblacion_af integer,
#     nombre text,
#     descripcion text
# );

class SubpoblacionAfectada(models.Model):
    id_subpoblacion_af = models.IntegerField()
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Subpoblación Afectada'
        verbose_name_plural = 'Subpoblaciones Afectadas'
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

class PoblacionesAfectadas(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    poblacion_afectada = models.ForeignKey(PoblacionAfectada, on_delete=models.CASCADE)
    subpoblacion_afectada = models.ForeignKey(SubpoblacionAfectada, on_delete=models.CASCADE)
    descripcion = models.TextField()
    interes = models.TextField()
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.poblacion_afectada.nombre
    
    class Meta:
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

class InteresesPoblacion(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    poblacion_afectada = models.ForeignKey(PoblacionAfectada, on_delete=models.CASCADE)
    interes = models.TextField()

    def __str__(self):
        return self.poblacion_afectada.nombre
    
    class Meta:
        verbose_name = 'Interés Población'
        verbose_name_plural = 'Intereses Poblaciones'
        db_table = 'intereses_poblacion'



# -- ======================== AFECTACIONES ================================


# --------------------- Afectaciones ecológicas --------------------------------

# CREATE TABLE ocs.cat_tipo_afectaciones_ecologicas (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoAfectacionesEcologicas(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
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
class AfectacionesEcologicas(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_ae = models.ForeignKey(TipoAfectacionesEcologicas, on_delete=models.CASCADE)
    descripcion_ae = models.TextField()
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    ubicaciones = models.ManyToManyField(Ubicacion, db_table='ocs.ae_to_ubicaciones')

    def __str__(self):
        return self.tipo_ae.nombre
    
    class Meta:
        verbose_name = 'Afectación Ecológica'
        verbose_name_plural = 'Afectaciones Ecológicas'
        db_table = 'afectaciones_ecologicas'


# --ubicaciones

# CREATE TABLE ocs.ae_to_ubicaciones (
#     id integer NOT NULL,
#     afectacion_ecologica_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );




# # --------------------- Afectaciones sociales --------------------------------

# CREATE TABLE ocs.cat_tipo_afectaciones_sociales (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class TipoAfectacionesSociales(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
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

class AfectacionesSociales(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_as = models.ForeignKey(TipoAfectacionesSociales, on_delete=models.CASCADE)
    descripcion_as = models.TextField()
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    ubicaciones = models.ManyToManyField(Ubicacion, db_table='ocs.as_to_ubicaciones')

    def __str__(self):
        return self.tipo_as.nombre
    
    class Meta:
        verbose_name = 'Afectación Social'
        verbose_name_plural = 'Afectaciones Sociales'
        db_table = 'afectaciones_sociales'

# # --ubicaciones

# CREATE TABLE ocs.as_to_ubicaciones (
#     id integer NOT NULL,
#     afectacion_social_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );


# # -- ======================== EVENTOS (VARIOS) ================================


# # --------------------- Violencias (eventos) --------------------------------


# CREATE TABLE ocs.cat_hechos_violencia (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class HechosViolencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Hecho Violencia'
        verbose_name_plural = 'Hechos Violencia'
        db_table = 'cat_hechos_violencia'


# CREATE TABLE ocs.cat_forma_hecho_violencia (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class FormaHechoViolencia(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Forma Hecho Violencia'
        verbose_name_plural = 'Formas Hecho Violencia'
        db_table = 'cat_forma_hecho_violencia'


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

class Violencia(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    hecho_violencia = models.ForeignKey(HechosViolencia, on_delete=models.CASCADE)
    forma_hecho_violencia = models.ForeignKey(FormaHechoViolencia, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)
    num_victimas = models.TextField()
    is_hombres = models.BooleanField()
    is_mujeres = models.BooleanField()
    condicion_mujeres_victimas = models.ForeignKey(CondicionMujerVictima, on_delete=models.CASCADE)
    sector_social_victima = models.ForeignKey(SectorSocial, on_delete=models.CASCADE)
    is_victima_dirigente = models.BooleanField()
    responsable_estatal_desc = models.TextField()
    responsable_no_estatal_desc = models.TextField()

    ubicaciones = models.ManyToManyField(Ubicacion, db_table='ocs.violencias_to_ubicaciones')
    opositores = models.ManyToManyField(Opositor, db_table='ocs.violencias_to_opositores')

    def __str__(self):
        return self.hecho_violencia.nombre
    
    class Meta:
        verbose_name = 'Violencia'
        verbose_name_plural = 'Violencias'
        db_table = 'violencias'


# CREATE TABLE ocs.violencias_to_opositores (
#     id integer NOT NULL,
#     violencia_id integer,  --ForeignKey
#     opositor_id integer  --ForeignKey
# );


# # --ubicaciones

# CREATE TABLE ocs.violencias_to_ubicaciones (
#     id integer NOT NULL,
#     violencia_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );

# # --------------------- Acciones colectivas (eventos) --------------------------------

# CREATE TABLE ocs.cat_forma_ac (
#     id integer NOT NULL,
#     nombre text,
#     descripcion text
# );

class FormaAC(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Forma Acción Colectiva'
        verbose_name_plural = 'Formas Acciones Colectivas'
        db_table = 'cat_forma_ac'


# CREATE TABLE ocs.cat_subforma_ac (
#     id integer NOT NULL,
#     id_forma_ac integer,
#     nombre text,
#     descripcion text
# );
class SubformaAC(models.Model):
    id_forma_ac = models.IntegerField()
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
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

class AccioneColectiva(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    forma_ac = models.ForeignKey(FormaAC, on_delete=models.CASCADE)
    subforma_ac = models.ForeignKey(SubformaAC, on_delete=models.CASCADE)
    temporalidad = models.ForeignKey(Temporalidad, on_delete=models.CASCADE)

    ubicaciones = models.ManyToManyField(Ubicacion, db_table='ocs.ac_to_ubicaciones')
    opositores = models.ManyToManyField(Opositor, through='OpositoresToAC')

    def __str__(self):
        return self.forma_ac.nombre
    
    class Meta:
        verbose_name = 'Acción Colectiva'
        verbose_name_plural = 'Acciones Colectivas'
        db_table = 'acciones_colectivas'


# CREATE TABLE ocs.grupos_apoyo (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_grupo_apoyo text,
#     nombre text,
#     interes text
# );

class GruposApoyo(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_grupo_apoyo = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    interes = models.TextField()

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Grupo Apoyo'
        verbose_name_plural = 'Grupos Apoyo'
        db_table = 'grupos_apoyo'

# # -- relacional a opositor (y acción colectiva)

# CREATE TABLE ocs.opositores_to_ac (
#     id integer NOT NULL,
#     opositor_id integer,  --ForeignKey
#     ac_id integer  --ForeignKey
# );

class OpositoresToAC(models.Model):
    opositor = models.ForeignKey(Opositor, on_delete=models.CASCADE)
    accione_colectiva = models.ForeignKey(AccioneColectiva, on_delete=models.CASCADE, db_column='ac_id')

    def __str__(self):
        return self.opositor.nombre
    
    class Meta:
        verbose_name = 'Opositor a Acción Colectiva'
        verbose_name_plural = 'Opositores a Acciones Colectivas'
        db_table = 'opositores_to_ac'

# # --ubicaciones

# CREATE TABLE ocs.ac_to_ubicaciones (
#     id integer NOT NULL,
#     accion_colectiva_id integer,  --ForeignKey
#     ubicacion_id integer  --ForeignKey
# );


# # -- ======================== OTROS QUE NO ENTIENDO BIEN ================================


# CREATE TABLE ocs.otros (
#     id integer NOT NULL,
#     nota_id integer,  --ForeignKey
#     proyecto_id integer NOT NULL,  --ForeignKey
#     tipo_propiedad text,
#     fortalecimiento_tejido_social text,
#     descripcion text
# );


class Otros(models.Model):
    nota = models.ForeignKey(Nota, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo_propiedad = models.CharField(max_length=100)
    fortalecimiento_tejido_social = models.TextField()
    descripcion = models.TextField()

    def __str__(self):
        return self.tipo_propiedad
    
    class Meta:
        verbose_name = 'Otro'
        verbose_name_plural = 'Otros'
        db_table = 'otros'
