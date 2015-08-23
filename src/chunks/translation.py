from modeltranslation.translator import translator, TranslationOptions

from .models import Chunk


class ChunkTranslationOptions(TranslationOptions):
    fields = ('title', 'content')
translator.register(Chunk, ChunkTranslationOptions)
