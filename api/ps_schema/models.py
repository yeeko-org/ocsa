from django.db import models

LEVEL_CHOICES = [
    ("primary", "Colección principal"),
    ("secondary", "Colección secundaria"),
    ("relational", "Colección relacional"),
    ("category_group", "Grupo de categorías"),
    ("category_type", "Tipo de categoría"),
    ("category_subtype", "Subtipo de categoría"),
]


class Collection(models.Model):
    snake_name = models.CharField(
        max_length=225, primary_key=True)
    level = models.CharField(
        max_length=40, choices=LEVEL_CHOICES, verbose_name="Nivel")
    order = models.SmallIntegerField(
        default=5, verbose_name="Orden")
    icon = models.CharField(
        max_length=225, blank=True, null=True, verbose_name="Ícono")
    color = models.CharField(
        max_length=225, blank=True, null=True, verbose_name="Color")
    help_text = models.TextField(
        blank=True, null=True, verbose_name="Texto de ayuda")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.snake_name

    class Meta:
        verbose_name = "Colección"
        verbose_name_plural = "1.1 Colecciones"
        ordering = ['order']
