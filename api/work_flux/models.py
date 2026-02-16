from django.db import models
from typing import Callable
# from django.db.models import JSONField


GROUP_CHOICES = [
    ("register", "Registro"),
    ("validation", "Validación"),
    ("location", "Ubicación"),
    ("retro", "Retroalimentación"),
]


class StatusControl(models.Model):
    name = models.CharField(max_length=120, primary_key=True)
    group = models.CharField(
        max_length=10, choices=GROUP_CHOICES,
        verbose_name="grupo de status", default="petition")
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
        default=True, verbose_name="Abierto a todxs")
    is_deleted = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.group} - {self.public_name}"

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