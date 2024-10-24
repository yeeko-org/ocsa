from django.contrib import admin

from .models import Note, NoteFile


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
