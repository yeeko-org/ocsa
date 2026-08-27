from django.db import models
from work_flux.models import StatusControl
from project.models import Project
from event.models import Event
from impact.models import Impact


def default_alternative_names():
    return []


class State(models.Model):
    inegi_code = models.CharField(max_length=2, verbose_name="Clave INEGI")
    name = models.CharField(max_length=50, verbose_name="Nombre")
    short_name = models.CharField(
        max_length=20, verbose_name="Nombre Corto",
        blank=True, null=True)
    code_name = models.CharField(
        max_length=6, verbose_name="Nombre Clave",
        blank=True, null=True)
    alternative_names = models.JSONField(
        default=default_alternative_names,
        verbose_name="Lista nombres alternativos",
        help_text="Ocupar para OCAMIS",
    )

    def __str__(self):
        return self.short_name or self.code_name or self.name

    class Meta:
        ordering = ["inegi_code"]
        verbose_name = "Entidad Federativa"
        verbose_name_plural = "Entidades Federativas"


class Municipality(models.Model):

    inegi_code = models.CharField(max_length=6, verbose_name="Clave INEGI")
    complete_code = models.CharField(
        max_length=8, verbose_name="Clave INEGI Completa")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    std_name = models.CharField(
        max_length=255, verbose_name="Nombre Estandarizado")
    state = models.ForeignKey(
        State, verbose_name="State",
        null=True, on_delete=models.CASCADE,
        related_name="municipalities")
    population = models.IntegerField(
        blank=True, null=True, verbose_name="Población")
    latitude = models.FloatField(
        blank=True, null=True, verbose_name="Latitud de cabecera")
    longitude = models.FloatField(
        blank=True, null=True, verbose_name="Longitud de cabecera")
    altitude = models.IntegerField(
        blank=True, null=True, verbose_name="Altitud de cabecera")
    # geometry = models.MultiPolygonField(
    #     null=True, blank=True, verbose_name="Límites territoriales",
    #     help_text="Polígonos que definen los límites del municipio")

    def __str__(self):
        return "%s - %s" % (self.name, self.state)

    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
        ordering = ["inegi_code"]


class Locality(models.Model):
    inegi_code = models.CharField(max_length=6, verbose_name="Clave INEGI")
    complete_code = models.CharField(
        max_length=12, verbose_name="Clave INEGI Completa")
    name = models.CharField(max_length=120, verbose_name="Nombre")
    municipality = models.ForeignKey(
        Municipality, verbose_name="Municipality",
        null=True, on_delete=models.CASCADE,
        related_name="localities")
    population = models.IntegerField(
        blank=True, null=True, verbose_name="Población")
    is_rural = models.BooleanField(default=False, verbose_name="Es rural")
    is_current = models.BooleanField(
        default=True, verbose_name="Vigente en el catálogo INEGI",
        help_text="Las localidades que el INEGI retiró se marcan como no "
                  "vigentes en vez de borrarse: hay ubicaciones antiguas "
                  "que las usan.")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    altitude = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.name, self.municipality)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"


# Tolerancia de referencia; cada capa se carga con la suya (ver
# `load_geometries`): a 50 m los municipios chicos de Oaxaca y Tlaxcala
# pierden más de 1 % de área, y las manchas urbanas aún más.
DEFAULT_SIMPLIFIED_M = 50


class GeometryBase(models.Model):
    """Polígono del INEGI en WKB, EPSG:6372 (Cónica Conforme de Lambert)."""

    wkb = models.BinaryField(verbose_name="Geometría (WKB, EPSG:6372)")
    simplified_m = models.SmallIntegerField(
        default=DEFAULT_SIMPLIFIED_M,
        verbose_name="Tolerancia de simplificación (m)")

    class Meta:
        abstract = True


class StateGeometry(GeometryBase):
    state = models.OneToOneField(
        State, on_delete=models.CASCADE, related_name="geometry",
        verbose_name="Entidad Federativa")

    def __str__(self):
        return f"Geometría de {self.state}"

    class Meta:
        verbose_name = "Geometría de entidad"
        verbose_name_plural = "Geometrías de entidades"


class MunicipalityGeometry(GeometryBase):
    municipality = models.OneToOneField(
        Municipality, on_delete=models.CASCADE, related_name="geometry",
        verbose_name="Municipio")

    def __str__(self):
        return f"Geometría de {self.municipality}"

    class Meta:
        verbose_name = "Geometría de municipio"
        verbose_name_plural = "Geometrías de municipios"


class LocalityGeometry(GeometryBase):
    """Manzanas de una localidad, fusionadas en un MultiPolygon."""

    locality = models.OneToOneField(
        Locality, on_delete=models.CASCADE, related_name="geometry",
        verbose_name="Localidad")

    def __str__(self):
        return f"Geometría de {self.locality}"

    class Meta:
        verbose_name = "Geometría de localidad"
        verbose_name_plural = "Geometrías de localidades"


TYPE_LOCATIONS = (
    ("point", "Punto"),
    ("polygon", "Polígono"),
    ("line", "Línea"),
)


class Location(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True,
        related_name="locations")
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, blank=True, null=True,
        related_name="locations")
    impact = models.ForeignKey(
        Impact, on_delete=models.CASCADE, blank=True, null=True,
        related_name="locations")
    state = models.ForeignKey(
        State, on_delete=models.CASCADE,
        related_name="locations", blank=True, null=True)
    municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE,
        related_name="locations", blank=True, null=True)
    locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE,
        related_name="locations", blank=True, null=True)
    municipalities = models.ManyToManyField(
        Municipality, blank=True, related_name="crossed_locations",
        verbose_name="Municipios que abarca",
        help_text="Se calcula al guardar a partir del trazo; no se "
                  "captura a mano.")
    nearby_localities = models.PositiveSmallIntegerField(
        blank=True, null=True,
        verbose_name="Localidades que toca o roza",
        help_text="Cuántas localidades corta el trazo o quedan dentro de "
                  "su margen de cercanía. Si es exactamente una, se llena "
                  "el campo Localidad; con cero o más de una queda vacío.")
    details = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geojson = models.JSONField(blank=True, null=True)
    type_location = models.CharField(
        max_length=10, choices=TYPE_LOCATIONS, default="point")
    ubicacion_id_ref = models.IntegerField(blank=True, null=True)
    status_location = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return f"{self.state or 'sin entidad'} - {self.details}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.project:
            from utils.universal import apply_project_status_location
            apply_project_status_location(self.project)

    def delete(self, *args, **kwargs):
        project = self.project
        result = super().delete(*args, **kwargs)
        if project:
            from utils.universal import apply_project_status_location
            apply_project_status_location(project)
        return result

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
