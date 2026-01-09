import re
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import requests

from project.models import Project, StatusProject
from utils.open_ai import JsonRequestOpenAI
from work_flux.models import StatusControl, CommentsMixin
from profile_auth.models import User
from pydantic import BaseModel, Field
import enum


class Source(models.Model):
    name = models.CharField(max_length=100)
    is_news = models.BooleanField(
        default=True, verbose_name='Es una fuente de noticias')
    main_url = models.CharField(max_length=100, blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = 'Fuente de información'
        verbose_name_plural = 'Fuentes de información'


def clean_text(text):
    slugify_text = slugify(text)
    cleaned_text = slugify_text.replace('-', ' ').replace('_', ' ')
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


class Note(CommentsMixin, models.Model):
    nota_id_ref = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    old_id = models.IntegerField(blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    slug_title = models.CharField(max_length=255, blank=True, null=True)
    # En teoría, tendría que haber 2 fuentes, La Jornada y Reforma,
    # pero sí hay más, pues hay que registrarlas, pero con is_news=False
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE,
        verbose_name='Fuente de información', related_name='notes')
    section = models.CharField(max_length=120, blank=True, null=True)
    pages = models.CharField(max_length=80, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    capture_date = models.DateField(blank=True, null=True)
    editor = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        related_name='editors2')
    editors = models.ManyToManyField(
        User, blank=True, related_name='editors')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        related_name='reviewers2')
    reviewers = models.ManyToManyField(
        User, blank=True, related_name='reviewers')
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    files: models.QuerySet["NoteFile"]
    status_register_id = str | None

    def set_slug_title(self, save=True):
        self.slug_title = clean_text(self.title)
        if save:
            self.save()

    def save(self, *args, **kwargs):
        if not self.capture_date:
            self.capture_date = timezone.now().date()
        if not self.slug_title:
            self.set_slug_title(save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Nota Final'
        verbose_name_plural = 'Notas Finales'


def upload_to_note_file(instance, filename):
    return f'note_file/{instance.note.pk}/{filename}'


class NoteFile(models.Model):
    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_to_note_file, max_length=255)
    old_ref = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save_file_from_url(self, url, file_name, save=False):
        from django.core.files.base import ContentFile
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            self.file.save(file_name, ContentFile(response.content), save=save)
            return True
        return False

    def __str__(self):
        return self.file.name if self.file else 'Archivo sin nombre'

    class Meta:
        verbose_name = 'Archivo de nota'
        verbose_name_plural = 'Archivos de nota'


class Mention(CommentsMixin, models.Model):
    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='mentions')
    # RICK: Aún no sé si esto debería ser not null
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='mentions')
    filled = models.BooleanField(default=False)
    date_filled = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.note} - {self.project}'

    class Meta:
        verbose_name = 'Mención de proyecto en nota'
        verbose_name_plural = 'Menciones de proyectos en notas'


class StatusHistory(models.Model):
    mention = models.ForeignKey(
        Mention, on_delete=models.CASCADE, related_name='status_history')
    status_project = models.ForeignKey(
        StatusProject, on_delete=models.CASCADE, blank=True, null=True,
        related_name='status_histories')
    date = models.DateField(blank=True, null=True)
    interval = models.DurationField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    type_temporalidad = models.CharField(
        max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.status_project)

    class Meta:
        verbose_name = 'Historial de estatus de proyecto'
        verbose_name_plural = 'Historiales de estatus de proyectos'


class ScrapedRecord(models.Model):
    STATUS_CHOICES = [
        ("get_sections", "Traer secciones"),
        ("record_articles", "Guardar artículos"),
        ("preclassify", "Preclasificar"),
        ("criteria", "Criterios"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    ]
    from_date = models.DateField()
    to_date = models.DateField()
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='scraped_records')
    scraped_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20, blank=True, null=True, choices=STATUS_CHOICES)

    data = models.JSONField(blank=True, null=True)
    errors = models.JSONField(blank=True, null=True)
    date_start = models.DateTimeField(
        blank=True, null=True, auto_now_add=True)
    date_end = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        related_name='scraped_records')

    @property
    def total_days(self):
        return (self.to_date - self.from_date).days + 1

    def __str__(self):
        return f"{self.source.name} - {self.from_date} to {self.to_date} ({self.status})"

    class Meta:
        verbose_name = 'Bloque de scrapeo'
        verbose_name_plural = 'Bloques de scrapeo'
        ordering = ['-from_date']


class DiscardedReason(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_other = models.BooleanField(default=False)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name


    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Razón de descarte'
        verbose_name_plural = 'Razones de descarte'


class ExtractivismTypes(enum.Enum):
    agro = "agro"
    mineria = "mineria"
    hidricos = "hidricos"
    energia = "energia"
    urbano = "urbano"
    infra = "infra"


class ProjectBase(BaseModel):
    name: str
    types: list[ExtractivismTypes] = []
    paragraphs: list[int] = []


class FeaturesBase(BaseModel):
    opponents: list[int]
    social_impacts: list[int]
    ecological_impacts: list[int]
    acts_of_violence: list[int]
    collective_actions: list[int]


class ProjectSelect(ProjectBase, FeaturesBase):
    is_specific_project: bool
    is_extractivist_or_big_scale: bool
    is_public_policy: bool
    is_political_opinion: bool
    is_labor_conflict_only: bool


class ArticleBase(FeaturesBase):
    projects: list[ProjectBase] = []
    is_foreign: bool | None = None
    is_political_opinion: bool | None = None


class ArticleRevision(BaseModel):
    projects: list[ProjectSelect] = []


class Article(models.Model):

    uid = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='articles')
    section = models.CharField(max_length=120, blank=True, null=True)
    url = models.CharField(max_length=255)
    # No entiendo por qué teníamos esto e images, según yo esto no va
    imgs = models.TextField(blank=True, null=True)
    basic_content = models.TextField(blank=True, null=True)
    scraped_date = models.DateField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)

    author = models.CharField(max_length=255, blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    paragraphs = models.JSONField(blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)

    criteria = models.JSONField(blank=True, null=True)
    certainty_degree = models.IntegerField(
        blank=True, null=True, verbose_name='Grado de certeza',
        help_text='Debe superar 100 para ser considerado')
    second_criteria = models.JSONField(blank=True, null=True)
    second_certainty_degree = models.IntegerField(
        blank=True, null=True, verbose_name='Grado de certeza (deep)',
        help_text='Debe superar 100 para ser considerado')

    is_selected = models.BooleanField(blank=True, null=True)
    discarded_reason = models.ForeignKey(
        DiscardedReason, on_delete=models.CASCADE, blank=True, null=True,
        related_name='articles')
    other_discarded_reason = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    status_retro = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)

    scraped = models.ForeignKey(
        ScrapedRecord, on_delete=models.CASCADE, related_name='articles')
    errors = models.JSONField(blank=True, null=True)

    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='articles',
        blank=True, null=True)

    def get_meta(self, key: str):
        return self.metadata.get(key) if self.metadata else None

    def get_certainty_degree_v2(self, criteria: type[ArticleBase] | None) -> int:

        if not criteria and self.criteria:
            criteria = ArticleBase(**self.criteria)

        if not criteria:
            return 0

        degree = 0
        if bool(criteria.projects):
            degree += 95
        degree += self.sum_degrees(criteria)

        if bool(criteria.is_political_opinion):
            if degree > 100:
                degree = 98
        if bool(criteria.is_foreign):
            if degree > 100:
                degree = 97
        return degree

    def sum_degrees(self, criteria: type[FeaturesBase]) -> int:
        total = 0
        feature_weights = {
            'opponents': 13,
            'social_impacts': 18,
            'ecological_impacts': 24,
            'acts_of_violence': 21,
            'collective_actions': 20,
        }
        for feature, weight in feature_weights.items():
            if getattr(criteria, feature):
                total += weight
        # if bool(criteria.opponents):
        #     total += 13
        # if bool(criteria.social_impacts):
        #     total += 18
        # if bool(criteria.ecological_impacts):
        #     total += 24
        # if bool(criteria.acts_of_violence):
        #     total += 21
        # if bool(criteria.collective_actions):
        #     total += 20
        return total

    def get_second_certainty_degree(self, criteria: dict | None) -> int:

        criteria = criteria or self.second_criteria

        if not criteria:
            return 0

        degrees = []
        fields = [
            ("is_specific_project", False),
            ("is_extractivist_or_big_scale", False),
            ("is_public_policy", True),
            ("is_political_opinion", True),
            ("is_labor_conflict_only", True)
        ]
        for project in criteria["projects"]:
            negatives = 0
            for field, failed_val in fields:
                if project.get(field) == failed_val:
                    negatives += 1
            if negatives > 0:
                project_degree = 100 - negatives
            else:
                project_like = ProjectSelect(**project)
                project_degree = 95 + self.sum_degrees(project_like)
            project["degrees"] = project_degree
            degrees.append(project_degree)

        return max(degrees) if degrees else 0

    def __str__(self):
        return f"{self.uid} - {self.title}"

    class Meta:
        unique_together = ['uid', 'source']
        verbose_name = 'Pre-Nota'
        verbose_name_plural = 'Pre-Notas'
        # ordering = ['-second_certainty_degree', '-certainty_degree', '-published_date']
        ordering = [
            models.F('second_certainty_degree').desc(nulls_last=True),
            '-certainty_degree',
            '-published_date'
        ]


class QualifySchema(models.Model):
    PROMPT_VERSION_CHOICES = [
        ('preclassify_v1', 'Preclasificación v1'),
        ('preclassify_v2', 'Preclasificación v2'),
        ('criteria_v1', 'Criterios v1'),
        ('criteria_v2', 'Criterios v2'),
    ]
    scraped_record = models.ForeignKey(
        ScrapedRecord, on_delete=models.CASCADE,
        related_name='schemas', blank=True, null=True)
    ia_model = models.CharField(max_length=255)
    prompt_version = models.CharField(
        max_length=20, choices=PROMPT_VERSION_CHOICES)
    batch_size = models.IntegerField()

    def __str__(self):
        return f"{self.ia_model} - {self.prompt_version} ({self.batch_size})"

    class Meta:
        verbose_name = 'Esquema de calificación'
        verbose_name_plural = 'Esquemas de calificación'


class ArticleQualify(models.Model):
    CHANGE_OPTIONS = [
        ('minus', 'Erróneamente excluido'),
        ('plus', 'Erróneamente incluido'),
        ('selected', 'Incluido correctamente'),
        ('not_selected', 'Excluido correctamente'),
    ]
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='qualifications')
    qualify_schema = models.ForeignKey(
        QualifySchema, on_delete=models.CASCADE, related_name='qualifications')
    is_selected = models.BooleanField(blank=True, null=True)

    criteria = models.JSONField(blank=True, null=True)
    certainty_degree = models.IntegerField(blank=True, null=True)
    change_value = models.CharField(
        max_length=20, choices=CHANGE_OPTIONS, blank=True, null=True)
    request_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.article} - {self.qualify_schema}"

    class Meta:
        verbose_name = 'Calificación de artículo'
        verbose_name_plural = 'Calificaciones de artículos'
