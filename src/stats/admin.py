from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from modeltranslation.admin import TranslationAdmin

from .models import Object, Profile, Tour, Mission, Score, Squad, Award


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.
    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    Source: https://gist.github.com/aaugustin/1388243
    """

    actions = None

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them
    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return False
        return super(ReadOnlyModelAdmin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('key', 'type', 'value', 'custom_value')
    fields = ('key', 'type', 'value', 'custom_value')
    readonly_fields = ('key', 'type', 'value')


@admin.register(Object)
class ObjectAdmin(TranslationAdmin):
    list_display = ('name', 'log_name', 'cls_base', 'cls', 'is_playable')
    list_filter = ('cls_base', 'cls', 'is_playable')
    readonly_fields = ('log_name', 'score', 'is_playable')

    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tour', 'date_start', 'date_end', 'duration', 'players_total', 'pilots_total',
                    'winning_coalition', 'preset', 'is_correctly_completed', 'is_hide')
    list_display_links = ('id', 'name')
    list_filter = ('winning_coalition', 'preset', 'is_correctly_completed', 'is_hide')
    readonly_fields = ('tour', 'name', 'path', 'date_start', 'date_end', 'duration', 'timestamp', 'players_total',
                       'pilots_total', 'gunners_total', 'winning_coalition', 'win_reason', 'preset', 'settings',
                       'is_correctly_completed', 'score_dict')

    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Tour)
class TourAdmin(TranslationAdmin):
    list_display = ('id', 'get_title', 'date_start', 'date_end', 'is_ended')
    list_display_links = ('id', 'get_title')
    list_filter = ('is_ended',)

    actions = None


@admin.register(Award)
class AwardAdmin(TranslationAdmin):
    list_display = ('title', 'func', 'type')
    list_display_links = ('title', 'func')
    ordering = ['type', 'func']


if settings.DEV_MODE:

    @admin.register(Profile)
    class ProfileAdmin(admin.ModelAdmin):
        list_display = ('id', 'nickname', 'uuid', 'is_hide')
        list_display_links = ('id', 'nickname',)
        list_filter = ('is_hide',)
        ordering = ('nickname',)
        readonly_fields = ('uuid',)
        search_fields = ('nickname', 'uuid')


    @admin.register(Squad)
    class SquadAdmin(admin.ModelAdmin):
        list_display = ('id', 'name', 'num_members')
        list_display_links = ('id', 'name')

else:

    @admin.register(Profile)
    class ProfileAdmin(admin.ModelAdmin):
        list_display = ('id', 'nickname', 'uuid', 'is_hide')
        list_display_links = ('id', 'nickname',)
        list_filter = ('is_hide',)
        ordering = ('nickname',)
        readonly_fields = ('uuid', 'nickname', 'user', 'squad')
        search_fields = ('nickname', 'uuid')

        actions = None

        def has_add_permission(self, request):
            return False

        def has_delete_permission(self, request, obj=None):
            return False
