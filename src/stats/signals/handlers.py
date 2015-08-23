from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete, post_save, post_delete
from django.dispatch.dispatcher import receiver

from squads.models import SquadMember, Squad as SquadProfile
from ..models import Profile, Squad, Tour


User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if instance.is_active and not hasattr(instance, 'profile'):
        try:
            profile = Profile.objects.get(nickname=instance.username)
            profile.connect_with_user(user=instance)
        except Profile.DoesNotExist:
            pass


@receiver(post_delete, sender=SquadMember)
def user_leave_squad(sender, instance, **kwargs):
    user = instance.member
    # проверяем есть ли профиль игрока, т.е. были ли вылеты на сервере
    if hasattr(user, 'profile'):
        user.profile.squad = None
        user.profile.save()
        # находим все стат профили игрока в неоконченных турах и убираем сквад у профиля
        user.profile.players.filter(tour__is_ended=False).update(squad=None)

        # находим все стат профили сквада в неоконченных турах и пересчитываем кол-во игроков
        for squad in instance.squad.stats.filter(tour__is_ended=False):
            squad.save()


@receiver(post_save, sender=SquadMember)
def user_join_squad(sender, instance, created, **kwargs):
    user = instance.member
    # проверяем есть ли профиль игрока, т.е. были ли вылеты на сервере
    if hasattr(user, 'profile'):
        user.profile.squad = instance.squad
        user.profile.save()
    # добавление в сквад производиться во время обработки миссии


@receiver(post_save, sender=SquadProfile)
def new_squad(sender, instance, created, **kwargs):
    if created:
        tour = Tour.objects.filter(is_ended=False).order_by('-id')[0]
        squad = Squad.objects.create(tour_id=tour.pk, profile_id=instance.pk)


@receiver(post_save, sender=Profile)
def profile_post_save(sender, instance, created, **kwargs):
    if instance.user and instance.nickname != instance.user.username:
        # на всякий случай проверяем нет ли другого юзера с таким новым именем
        another_user = User.objects.exclude(id=instance.user.id).filter(username=instance.nickname)
        # если есть - переименовываем его
        if another_user:
            another_user[0].username = 'renamed_user_{id}'.format(id=another_user[0].id)
            another_user[0].save()
        instance.user.username = instance.nickname
        instance.user.save()
