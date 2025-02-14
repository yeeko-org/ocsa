from django.contrib import admin

from .models import Note, NoteFile, ScrapedRecord, Article, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass


class NoteFileInline(admin.TabularInline):
    model = NoteFile
    extra = 0


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    inlines = [NoteFileInline]
    list_display = ['title', 'id', 'nota_id_ref', 'date', 'source']
    search_fields = ['title', 'nota_id_ref']
    list_filter = ['source']
    ordering = ['date']


@admin.register(ScrapedRecord)
class ScrapedRecordAdmin(admin.ModelAdmin):
    list_display = ['pk', 'source', 'from_date', 'to_date', 'scraped_date']
    list_filter = ['source']
    ordering = ['scraped_date']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'preclasification',
                    'source', 'scraped_date', 'url']
    search_fields = ['title']
    list_filter = ['source', "scraped", "preclasification"]
    ordering = ['scraped_date']
