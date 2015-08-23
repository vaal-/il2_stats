from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _

from .models import Squad, SquadMember


class SquadMemberInline(admin.TabularInline):
    model = SquadMember


if settings.DEV_MODE:

    @admin.register(Squad)
    class SquadAdmin(admin.ModelAdmin):
        list_display = ('name', 'tag')
        search_fields = ('name', 'tag')
        inlines = (SquadMemberInline,)


    @admin.register(SquadMember)
    class SquadMemberAdmin(admin.ModelAdmin):
        list_display = ('squad', 'member', 'date_joined', 'is_admin')
        list_filter = ('is_admin',)
else:

    @admin.register(Squad)
    class SquadAdmin(admin.ModelAdmin):
        list_display = ('name', 'tag')
        search_fields = ('name', 'tag')

        actions = None

        def has_add_permission(self, request):
            return False

        def has_delete_permission(self, request, obj=None):
            return False
