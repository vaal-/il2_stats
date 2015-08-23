from modeltranslation.translator import translator, TranslationOptions

from .models import Object, Tour, Award


class ObjectTranslationOptions(TranslationOptions):
    fields = ('name', )

translator.register(Object, ObjectTranslationOptions)


class TourTranslationOptions(TranslationOptions):
    fields = ('title', )

translator.register(Tour, TourTranslationOptions)


class AwardTranslationOptions(TranslationOptions):
    fields = ('title', 'desc')

translator.register(Award, AwardTranslationOptions)
