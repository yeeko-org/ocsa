from django.db import models
from work_flux.models import StatusControl


class CatalogBase(models.Model):
    name = models.CharField(max_length=160)
    order = models.SmallIntegerField(default=10)
    description = models.TextField(blank=True, null=True)
    help_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        abstract = True


class CatalogGroup(CatalogBase):
    icon = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['order']
        abstract = True


class CatalogType(CatalogBase):
    comments = models.TextField(blank=True, null=True)
    status_validation = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['order']
        abstract = True
