from django.db import models

from notes.models import Nota
from projects.models import Proyecto


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
