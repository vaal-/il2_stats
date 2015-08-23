from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


SQUAD_MEMBERS_MINIMUM = settings.SQUAD_MEMBERS_MINIMUM


class SquadQuerySet(models.QuerySet):
    def active(self):
        return self.filter(num_members__gte=SQUAD_MEMBERS_MINIMUM)

    def search(self, name):
        return self.filter(Q(profile__name__icontains=name) | Q(profile__tag__icontains=name))


class SquadManager(models.Manager):
    def get_queryset(self):
        return (SquadQuerySet(model=self.model, using=self._db, hints=self._hints)
                .exclude(profile__is_removed=True).select_related('profile'))

    def active(self):
        return self.get_queryset().active()

    def search(self, name):
        return self.get_queryset().search(name=name)


class PlayerQuerySet(models.QuerySet):
    def pilots(self, *args, **kwargs):
        return self.filter(type='pilot', *args, **kwargs)

    def gunners(self, *args, **kwargs):
        return self.filter(type='gunner', *args, **kwargs)

    def active(self, tour):
        if settings.INACTIVE_PLAYER_DAYS:
            if tour.is_ended:
                date = tour.date_end - settings.INACTIVE_PLAYER_DAYS
            else:
                date = timezone.now() - settings.INACTIVE_PLAYER_DAYS
            return self.filter(date_last_combat__gt=date, tour_id=tour.id)
        else:
            return self.filter(tour_id=tour.id)

    def search(self, name):
        return self.filter(profile__nickname__icontains=name)


class PlayerManager(models.Manager):
    def get_queryset(self):
        return (PlayerQuerySet(model=self.model, using=self._db, hints=self._hints)
                .exclude(profile__is_hide=True).select_related('profile', 'tour'))

    def pilots(self, *args, **kwargs):
        return self.get_queryset().pilots(*args, **kwargs)

    def gunners(self, *args, **kwargs):
        return self.get_queryset().gunners(*args, **kwargs)

    def active(self, tour):
        return self.get_queryset().active(tour=tour)

    def search(self, name):
        return self.get_queryset().search(name=name)
