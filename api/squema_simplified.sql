

-- ======================== CATS GENERALES ================================


--- formas de organización y población


CREATE TABLE ocs.cat_sector_social (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


-- Otros cats:


CREATE TABLE ocs.cat_condicion_mujer_victima (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


---------------- Extensión de temporalidad (Para varios) -----------------



CREATE TABLE ocs.cat_temporalidad (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.temporalidad (
    id integer NOT NULL,
    fecha date,
    intervalo interval,
    day_undefined boolean DEFAULT false,
    month_undefined boolean DEFAULT false,
    cat_temporalidad_id integer  --ForeignKey
);



--------------------- Ubicaciones (para varias)--------------------------------



CREATE TABLE ocs.ubicaciones (
    id integer NOT NULL,
    tipo_ubicacion ocs.tipo_ubicacion_e DEFAULT 'punto'::ocs.tipo_ubicacion_e,
    estado text,
    municipio text,
    localidad text,
    especificaciones text,
    sitio text,
    latitud double precision,
    longitud double precision,
    geom text
);



-- ========================= NOTAS   =============================


CREATE TABLE ocs.notas (
    id integer NOT NULL,
    id_nota integer,
    titulo text,
    autor text,
    nombre_medio text,
    pagina_medio text,
    vinculo text,
    fecha date,
    fecha_captura date
);


-- No entiendo muy bien los siguientes 2 comandos:


CREATE TABLE ocs.registro_notas (
    id integer NOT NULL,
    owner text,
    datum jsonb,
    status ocs.draft_status DEFAULT 'inprogress'::ocs.draft_status,
    last_edit timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE ocs.registro_notas ENABLE ROW LEVEL SECURITY;




-- ===================== PROYECTOS Y CONFLICTOS  =============================


--------------------- Conflictos SocioAmbientales ---------------------------


CREATE TABLE ocs.csa (
    id integer NOT NULL,
    nombre text
);


------------------------------ Proyectos --------------------------------


-- Clasificaciones de proyecto


CREATE TABLE ocs.cat_tipo_despliegue_capital (
    id integer NOT NULL,
    nombre text,
    descripcion text,
    icono text,
    color text
);


CREATE TABLE ocs.cat_tipo_megaproyecto (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.cat_estatus_proyecto (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.proyectos (
    id integer NOT NULL,
    id_mp integer,
    nombre text,
    escala text,
    tipo_despliegue_capital_id integer,  --ForeignKey
    tipo_megaproyecto_id integer,  --ForeignKey
    especificaciones text,
    csa_id integer,  --ForeignKey
    proyecto_vinculado_id integer,  --ForeignKey
    old_ubis bigint
);


CREATE TABLE ocs.estatus_proyectos (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    estatus_id integer,  --ForeignKey
    temporalidad_id integer  --ForeignKey
);

--ubicaciones

CREATE TABLE ocs.proyectos_to_ubicaciones (
    id bigint NOT NULL,
    proyecto_id bigint,
    ubicacion_id bigint
);



-- ======================== ACTORES (VARIOS) ================================


--------------------- Capitalistas (actores) --------------------------------



CREATE TABLE ocs.capital (
    id integer NOT NULL,
    proyecto_id integer NOT NULL,  --ForeignKey
    nota_id integer,  --ForeignKey
    nombre text,
    matriz text,
    filial text,
    directores text,
    inversionistas text,
    nacionalidad text,
    is_capital_publico boolean,
    is_cotiza_bolsa boolean,
    interes text,
    is_activo boolean
);


------------------ Instituciones del estado (actores) ------------------------


CREATE TABLE ocs.estado (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    instituciones_a_favor_proyecto text,
    instituciones_mediadoras text,
    instituciones_atienden_reclamos text,
    temporalidad_id integer  --ForeignKey
);


--------------------- Opositores (actores) --------------------------------

-- cats

CREATE TABLE ocs.cat_forma_organizacion (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.cat_mujer (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


-- opositores

CREATE TABLE ocs.opositores (
    id integer NOT NULL,
    nombre text,
    forma_organizacion_id integer,  --ForeignKey
    is_indigena boolean,
    pueblo_indigena text,
    is_campesino_or_comunero_or_ejidatario boolean,
    mujer_id integer,  --ForeignKey
    is_trabajador_empresa boolean,
    otros_opositores text,
    is_habitante_zona boolean
);


-- relacionales

CREATE TABLE ocs.opositores_to_proyecto (
    id integer NOT NULL,
    opositor_id integer,  --ForeignKey
    proyecto_id integer  --ForeignKey
);


CREATE TABLE ocs.opositores_to_notas (
    id integer NOT NULL,
    opositor_id integer,  --ForeignKey
    nota_id integer  --ForeignKey
);

--ubicaciones

CREATE TABLE ocs.opositores_to_ubicaciones (
    id integer NOT NULL,
    opositor_id integer,  --ForeignKey
    ubicacion_id integer  --ForeignKey
);

-- Intereses

CREATE TABLE ocs.intereses_opositores (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    opositor_id integer,  --ForeignKey
    interes text
);



--------------------- Poblaciones (actores) --------------------------------

-- Cats

CREATE TABLE ocs.cat_poblacion_afectada (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.cat_subpoblacion_afectada (
    id integer NOT NULL,
    id_subpoblacion_af integer,
    nombre text,
    descripcion text
);

-- Poblaciones

CREATE TABLE ocs.poblaciones_afectadas (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    poblacion_afectada_id integer,  --ForeignKey
    subpoblacion_afectada_id integer,  --ForeignKey
    descripcion text,
    interes text,
    ubicacion_id integer  --ForeignKey
);


-- intereses

CREATE TABLE ocs.intereses_poblacion (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    poblacion_afectada_id integer,  --ForeignKey
    interes text
);



-- ======================== AFECTACIONES ================================


--------------------- Afectaciones ecológicas --------------------------------

CREATE TABLE ocs.cat_tipo_afectaciones_ecologicas (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.afectaciones_ecologicas (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    tipo_ae_id integer,  --ForeignKey
    descripcion_ae text,
    temporalidad_id integer  --ForeignKey
);


--ubicaciones

CREATE TABLE ocs.ae_to_ubicaciones (
    id integer NOT NULL,
    afectacion_ecologica_id integer,  --ForeignKey
    ubicacion_id integer  --ForeignKey
);


--------------------- Afectaciones sociales --------------------------------

CREATE TABLE ocs.cat_tipo_afectaciones_sociales (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.afectaciones_sociales (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    tipo_as_id integer,  --ForeignKey
    descripcion_as text,
    temporalidad_id integer  --ForeignKey
);

--ubicaciones

CREATE TABLE ocs.as_to_ubicaciones (
    id integer NOT NULL,
    afectacion_social_id integer,  --ForeignKey
    ubicacion_id integer  --ForeignKey
);


-- ======================== EVENTOS (VARIOS) ================================


--------------------- Violencias (eventos) --------------------------------


CREATE TABLE ocs.cat_hechos_violencia (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.cat_forma_hecho_violencia (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.violencias (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    hecho_violencia_id integer,  --ForeignKey
    forma_hecho_violencia_id integer,  --ForeignKey
    temporalidad_id integer,  --ForeignKey
    num_victimas text,
    is_hombres boolean,
    is_mujeres boolean,
    condicion_mujeres_victimas integer,
    sector_social_victima integer,
    is_victima_dirigente boolean,
    responsable_estatal_desc text,
    responsable_no_estatal_desc text
);


CREATE TABLE ocs.violencias_to_opositores (
    id integer NOT NULL,
    violencia_id integer,  --ForeignKey
    opositor_id integer  --ForeignKey
);


--ubicaciones

CREATE TABLE ocs.violencias_to_ubicaciones (
    id integer NOT NULL,
    violencia_id integer,  --ForeignKey
    ubicacion_id integer  --ForeignKey
);

--------------------- Acciones colectivas (eventos) --------------------------------

CREATE TABLE ocs.cat_forma_ac (
    id integer NOT NULL,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.cat_subforma_ac (
    id integer NOT NULL,
    id_forma_ac integer,
    nombre text,
    descripcion text
);


CREATE TABLE ocs.acciones_colectivas (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    forma_ac_id integer,  --ForeignKey
    subforma_ac_id integer,  --ForeignKey
    temporalidad_id integer  --ForeignKey
);



CREATE TABLE ocs.grupos_apoyo (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    tipo_grupo_apoyo text,
    nombre text,
    interes text
);

-- relacional a opositor (y acción colectiva)

CREATE TABLE ocs.opositores_to_ac (
    id integer NOT NULL,
    opositor_id integer,  --ForeignKey
    ac_id integer  --ForeignKey
);

--ubicaciones

CREATE TABLE ocs.ac_to_ubicaciones (
    id integer NOT NULL,
    accion_colectiva_id integer,  --ForeignKey
    ubicacion_id integer  --ForeignKey
);


-- ======================== OTROS QUE NO ENTIENDO BIEN ================================


CREATE TABLE ocs.otros (
    id integer NOT NULL,
    nota_id integer,  --ForeignKey
    proyecto_id integer NOT NULL,  --ForeignKey
    tipo_propiedad text,
    fortalecimiento_tejido_social text,
    descripcion text
);

