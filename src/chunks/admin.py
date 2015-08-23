from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Chunk


@admin.register(Chunk)
class ChunkAdmin(TranslationAdmin):
    list_display = ('key', 'title')
    search_fields = ('key', 'title', 'content')
