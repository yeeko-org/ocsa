from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    flag_emoji = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class StatusProject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Status Project'
        verbose_name_plural = 'Status Projects'
