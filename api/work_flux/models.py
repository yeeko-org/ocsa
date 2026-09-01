from django.db import models
from typing import Callable


class StatusGroup(models.Model):
    key_name = models.CharField(max_length=30, primary_key=True)
    public_name = models.CharField(max_length=120)
    order = models.IntegerField(default=0)
    hidden = models.BooleanField(
        default=False, verbose_name="oculto en la barra de filtros")
    # El chip del grupo no se pinta si el registro no trae status; hoy
    # solo retro, que es opcional en todas las colecciones.
    hide_when_empty = models.BooleanField(default=False)

    @property
    def field_name(self) -> str:
        """Nombre del FK a StatusControl que lleva este grupo.

        La convención `status_<key_name>` la comparten los modelos, los
        filtros del front y las claves de ordenamiento; no es un dato
        editable, así que se deriva en vez de guardarse.
        """
        return f"status_{self.key_name}"

    def __str__(self) -> str:
        return self.public_name

    class Meta:
        ordering = ["order"]
        verbose_name = "Grupo de status"
        verbose_name_plural = "Grupos de status"


class StatusControl(models.Model):
    name = models.CharField(max_length=120, primary_key=True)
    group = models.ForeignKey(
        StatusGroup, on_delete=models.PROTECT, related_name="statuses",
        verbose_name="grupo de status", default="validation")
    public_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(
        max_length=30, blank=True, null=True,
        help_text="https://vuetifyjs.com/en/styles/colors/")
    icon = models.CharField(
        max_length=40, blank=True, null=True,
        help_text="https://fonts.google.com/icons")
    order = models.IntegerField(default=4)
    is_public = models.BooleanField(default=True)
    open_editor = models.BooleanField(
        default=True, verbose_name="edición abierta",
        help_text="Los registros que están en este status pueden editarse "
                  "—y cambiarse de status— por cualquier editor; apagado, "
                  "solo los editores plenos y el staff.")
    open_selectable = models.BooleanField(
        default=True, verbose_name="seleccionable como destino",
        help_text="Este status puede elegirse como nuevo status al "
                  "capturar; apagado, solo los editores plenos y el staff "
                  "pueden asignarlo (p. ej. status heredados de la v.1 o "
                  "de uso interno).")
    is_legacy = models.BooleanField(
        default=False, verbose_name="status legacy",
        help_text="Ya no participa del flujo vivo: no se asigna ni se "
                  "ofrece; se conserva porque hay registros históricos "
                  "que lo usan.")
    priority = models.IntegerField(default=0)

    def __str__(self):
        # `group_id` y no `group`: conserva la salida previa al FK y evita
        # una consulta por fila en los desplegables del admin.
        return f"{self.group_id} - {self.public_name}"

    class Meta:
        ordering = ["group", "order"]
        verbose_name = "Status de control"
        verbose_name_plural = "Status de control (TODOS)"


class CommentsMixin(models.Model):
    comments = models.TextField(blank=True, null=True)

    def add_comment(self, comment: str):
        if not comment:
            return
        if self.comments:
            if comment not in self.comments:
                self.comments += f"\n\n{comment}"
        else:
            self.comments = comment
        self.save()

    class Meta:
        abstract = True
