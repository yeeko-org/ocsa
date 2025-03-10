import re
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from project.models import Project, StatusProject
from work_flux.models import StatusControl, CommentsMixin
from profile_auth.models import User


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
        related_name='editors')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        related_name='reviewers')
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
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


def upload_to_note_file(instance, filename):
    return f'note_file/{instance.note.pk}/{filename}'


class NoteFile(models.Model):
    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=upload_to_note_file, max_length=255)
    old_ref = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

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
    # status_register = models.ForeignKey(
    #     StatusControl, on_delete=models.CASCADE, blank=True, null=True)
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
        StatusProject, on_delete=models.CASCADE, blank=True, null=True)
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
    preclassification = models.JSONField(blank=True, null=True)


class Article(models.Model):

    PRECLASSIFICATION_CHOICES = [
        ('invalid', 'Invalido'),
        ('valid', 'Valido'),
        ('maybe', 'Podría ser'),
        ('indirect', 'Indirecto'),
        ('unknown', 'Desconocido'),
    ]

    uid = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True)
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name='articles')
    section = models.CharField(max_length=120, blank=True, null=True)
    url = models.CharField(max_length=255)
    # No entiendo por qué teníamos esto e images, según yo esto no va
    imgs = models.TextField(blank=True, null=True)
    basic_content = models.TextField(blank=True, null=True)
    scraped_date = models.DateField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)

    preclassification = models.CharField(
        max_length=10, choices=PRECLASSIFICATION_CHOICES,
        blank=True, null=True)

    autor = models.CharField(max_length=255, blank=True, null=True)
    html_content = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)

    criteria = models.JSONField(blank=True, null=True)
    certainty_degree = models.IntegerField(blank=True, null=True)
    is_selected = models.BooleanField(blank=True, null=True)

    scraped = models.ForeignKey(
        ScrapedRecord, on_delete=models.CASCADE, related_name='articles')

    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='articles',
        blank=True, null=True)

    def get_certainty_degree(self, criteria: dict = None) -> int:
        criteria = criteria or self.criteria
        if not criteria:
            return 0

        degree = 0
        if bool(criteria.get("projects", [])):
            degree += 10
        if bool(criteria.get("has_opponents")):
            degree += 1
        if bool(criteria.get("social_impacts")):
            degree += 2
        if bool(criteria.get("ecological_impacts")):
            degree += 2
        if bool(criteria.get("acts_of_violence")):
            degree += 2
        if bool(criteria.get("collective_actions")):
            degree += 2

        if bool(criteria.get("is_foreign")):
            degree *= -1
        return degree

    def __str__(self):
        return f"{self.uid} - {self.title}"

    class Meta:
        unique_together = ['uid', 'source']


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
        return f"{self.article} - {self.ia_model}"

    class Meta:
        verbose_name = 'Calificación de artículo'
        verbose_name_plural = 'Calificaciones de artículos'
