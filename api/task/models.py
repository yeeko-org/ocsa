from django.db import models
from profile_auth.models import User
from source.models import Note, Article
from project.models import Project
from space_time.models import Location


class ClickHistory(models.Model):

    CLICK_ACTIONS = [
        ('opened', 'Abrió'),
        ('created', 'Creó'),
        ('updated', 'Guardó'),
        ('mention_child', 'Agregó a nota')
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name="Usuario", related_name="clicks")
    date_start = models.DateTimeField(verbose_name="Fecha", auto_now_add=True)
    action = models.CharField(
        max_length=20, choices=CLICK_ACTIONS, verbose_name="Acción",
        default='open')

    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name="Nota", related_name="clicks")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name="Artículo", related_name="clicks")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name="Proyecto", related_name="clicks")
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name="Ubicación", related_name="clicks")

    def __str__(self):
        return "%s - %s" % (self.user, self.date_start)

    class Meta:
        verbose_name = "Historial"
        verbose_name_plural = "Historial"
        ordering = ["-date_start"]


OFFLINE_TYPES = (
    ('weekly_meeting', 'Reunión semanal'),
    ('meeting', 'Reunión'),
    ('training', 'Capacitación'),
    ('other', 'Otro'),
)

class OfflineTask(models.Model):


    users = models.ManyToManyField(User, related_name="offline_tasks")
    date_start = models.DateTimeField(verbose_name="Inicio")
    date_end = models.DateTimeField(verbose_name="Fin")
    activity_type = models.CharField(
        max_length=100, choices=OFFLINE_TYPES, verbose_name="Tipo")
    name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Actividad")
    user_added = models.ForeignKey(
        User, blank=True, null=True,
        on_delete=models.DO_NOTHING, related_name="offline_tasks_added")

    def __str__(self):
        return "%s - %s" % (self.date_start, self.date_end)

    class Meta:
        verbose_name = "Tarea offline"
        verbose_name_plural = "Tareas offline"
        ordering = ["-date_start"]
