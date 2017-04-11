from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import validate_image_file_extension
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from stuff.storage import OverwriteStorage


def get_join_code():
    return get_random_string(length=40)


def squad_logo_path(instance, filename):
    return 'squads/{squad_id}'.format(squad_id=instance.id)


class Squad(models.Model):
    name = models.CharField(_('squad name'), max_length=256)
    tag = CICharField(_('squad tag'), max_length=16)  # TODO добавить индекс?
    website = models.URLField(_('website'), blank=True)
    about = models.TextField(_('about squad'), blank=True, max_length=500)
    logo = models.ImageField(_('squad logo'), upload_to=squad_logo_path, blank=True,
                             storage=OverwriteStorage(), validators=[validate_image_file_extension])
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='SquadMember')
    join_code = models.CharField(max_length=40, editable=False, default=get_join_code)
    is_removed = models.BooleanField(default=False)

    class Meta:
        db_table = 'squads'
        verbose_name = _('squad')
        verbose_name_plural = _('squads')

    def __str__(self):
        return self.name

    def get_join_url(self):
        return reverse('squads:join', kwargs={'squad_id': self.pk, 'code': self.join_code})

    def regenerate_join_code(self):
        self.join_code = get_join_code()
        self.save()

    def remove(self):
        self.is_removed = True
        self.save()
        for member in SquadMember.objects.filter(squad_id=self.pk):
            member.kick_from_squad()


class SquadMember(models.Model):
    member = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  primary_key=True, related_name='squad_member')
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    class Meta:
        db_table = 'squads_members'
        verbose_name = _('squad member')
        verbose_name_plural = _('squads members')

    def __str__(self):
        return '{member} ({squad})'.format(member=self.member, squad=self.squad)

    def leave_squad(self):
        self.kick_from_squad()

    def kick_from_squad(self):
        self.delete()

    def give_admin_role(self):
        self.is_admin = True
        self.save()

    def remove_admin_role(self):
        self.is_admin = False
        self.save()
