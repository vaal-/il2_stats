from calendar import monthrange
import hashlib

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.templatetags.static import static
from django.db import connection, models
from django.db.models import Avg, Count, Sum
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from mission_report.constants import Coalition, Country
from mission_report.statuses import BotLifeStatus, SortieStatus, LifeStatus, VLifeStatus

from .aircraft_mods import get_aircraft_mods
from .aircraft_payloads import get_aircraft_payload
from .models_managers import PlayerManager, SquadManager, VLifeManager
from .sql import get_position_by_field, get_squad_position_by_field


def default_coal_list():
    return [0, 0, 0]


def default_ammo():
    return {
        'used_cartridges': 0, 'used_bombs': 0, 'used_rockets': 0, 'used_shells': 0,
        'hit_bullets': 0, 'hit_bombs': 0, 'hit_rockets': 0, 'hit_shells': 0,
    }


def default_sorties_cls():
    return {
        'aircraft_light': 0, 'aircraft_medium': 0, 'aircraft_heavy': 0, 'aircraft_transport': 0,
        'aircraft_turret': 0,
    }


class Score(models.Model):
    SCORE_TYPE = (
        ('int', 'integer'),
        ('pct', 'percent'),
    )
    key = models.CharField(max_length=24, editable=False)
    type = models.CharField(max_length=3, choices=SCORE_TYPE, editable=False, default='int')
    value = models.IntegerField(default=0, editable=False)
    custom_value = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'scoring'
        ordering = ['key']
        verbose_name = _('score')
        verbose_name_plural = _('scoring')

    def __str__(self):
        return '{key} [{value}]'.format(key=self.key, value=self.get_value())

    def get_value(self):
        if self.custom_value is not None:
            return self.custom_value
        else:
            return self.value


class Object(models.Model):
    CLASSES = (
        ('aaa_heavy', 'aaa_heavy'),
        ('aaa_light', 'aaa_light'),
        ('aaa_mg', 'aaa_mg'),
        ('aerostat', 'aerostat'),
        ('aircraft_gunner', 'aircraft_gunner'),
        ('aircraft_heavy', 'aircraft_heavy'),
        ('aircraft_light', 'aircraft_light'),
        ('aircraft_medium', 'aircraft_medium'),
        ('aircraft_pilot', 'aircraft_pilot'),
        ('aircraft_static', 'aircraft_static'),
        ('aircraft_transport', 'aircraft_transport'),
        ('aircraft_turret', 'aircraft_turret'),
        ('armoured_vehicle', 'armoured_vehicle'),
        ('artillery_field', 'artillery_field'),
        ('artillery_howitzer', 'artillery_howitzer'),
        ('artillery_rocket', 'artillery_rocket'),
        ('block', 'block'),
        ('bomb', 'bomb'),
        ('building_big', 'building_big'),
        ('building_medium', 'building_medium'),
        ('building_small', 'building_small'),
        ('bullet', 'bullet'),
        ('car', 'car'),
        ('driver', 'driver'),
        ('explosion', 'explosion'),
        ('locomotive', 'locomotive'),
        ('machine_gunner', 'machine_gunner'),
        ('parachute', 'parachute'),
        ('rocket', 'rocket'),
        ('searchlight', 'searchlight'),
        ('ship', 'ship'),
        ('ship_heavy', 'ship_heavy'),
        ('ship_light', 'ship_light'),
        ('ship_medium', 'ship_medium'),
        ('shell', 'shell'),
        ('tank_heavy', 'tank_heavy'),
        ('tank_light', 'tank_light'),
        ('tank_medium', 'tank_medium'),
        ('tank_driver', 'tank_driver'),
        ('tank_turret', 'tank_turret'),
        ('trash', 'trash'),
        ('truck', 'truck'),
        ('vehicle_crew', 'vehicle_crew'),
        ('vehicle_static', 'vehicle_static'),
        ('vehicle_turret', 'vehicle_turret'),
        ('wagon', 'wagon'),
    )
    CLASSES_BASE = (
        ('aircraft', 'aircraft'),
        ('ammo', 'ammo'),
        ('block', 'block'),
        ('crew', 'crew'),
        ('turret', 'turret'),
        ('vehicle', 'vehicle'),
    )

    name = models.CharField(max_length=64, blank=True)
    log_name = models.CharField(max_length=64, editable=False, unique=True)
    cls_base = models.CharField(choices=CLASSES_BASE, max_length=24, blank=True)
    cls = models.CharField(choices=CLASSES, max_length=24, blank=True)
    score = models.ForeignKey(Score, on_delete=models.CASCADE)
    is_playable = models.BooleanField(default=False, editable=False)

    class Meta:
        db_table = 'objects'
        ordering = ['name']
        verbose_name = _('object')
        verbose_name_plural = _('objects')

    def __str__(self):
        return self.name

    def aircraft_image(self):
        return static('img/aircraft/{log_name}.png'.format(log_name=self.log_name))


class Tour(models.Model):
    title = models.CharField(max_length=32, blank=True)
    date_start = models.DateTimeField(default=timezone.now, db_index=True)
    date_end = models.DateTimeField(null=True, blank=True)
    is_ended = models.BooleanField(default=False)

    COALITIONS = (
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )
    winning_coalition = models.IntegerField(choices=COALITIONS, blank=True, null=True)

    class Meta:
        db_table = 'tours'
        ordering = ['-id']
        verbose_name = _('tour')
        verbose_name_plural = _('tours')

    def __str__(self):
        return self.get_title()

    def save(self, *args, **kwargs):
        if self.is_ended and not self.date_end:
            self.date_end = timezone.now()
        self.update_winning_coalition()
        super().save(*args, **kwargs)

    def update_winning_coalition(self):
        wins = self.missions_wins()
        coal_1_wins, coal_2_wins = wins[1], wins[2]
        if coal_1_wins > coal_2_wins:
            self.winning_coalition = 1
        elif coal_1_wins < coal_2_wins:
            self.winning_coalition = 2
        else:
            self.winning_coalition = None

    def missions_wins(self):
        wins = (self.missions.values('winning_coalition').order_by().annotate(num=Count('winning_coalition')))
        wins = {d['winning_coalition']: d['num'] for d in wins}
        return {
            1: wins.get(1, 0),
            2: wins.get(2, 0)
        }

    def stats_summary_total(self):
        summary_total = {'ak_total': 0, 'gk_total': 0, 'score': 0, 'flight_time': 0}
        _summary_total = (Sortie.objects
                          .filter(tour_id=self.id, is_disco=False)
                          .aggregate(ak_total=Sum('ak_total'), gk_total=Sum('gk_total'),
                                     score=Sum('score'), flight_time=Sum('flight_time')))
        summary_total.update(_summary_total)
        return summary_total

    def stats_summary_coal(self):
        summary_coal = {
            1: {'ak_total': 0, 'gk_total': 0, 'score': 0, 'flight_time': 0},
            2: {'ak_total': 0, 'gk_total': 0, 'score': 0, 'flight_time': 0},
        }
        _summary_coal = (Sortie.objects
                         .filter(tour_id=self.id, is_disco=False)
                         .values('coalition')
                         .order_by()
                         .annotate(ak_total=Sum('ak_total'), gk_total=Sum('gk_total'),
                                   score=Sum('score'), flight_time=Sum('flight_time')))
        for s in _summary_coal:
            summary_coal[s['coalition']].update(s)
        return summary_coal

    def coal_active_players(self):
        coal = {0: 0, 1: 0, 2: 0}
        active_players = (Player.players
                          .pilots(tour_id=self.id)
                          .active(tour=self)
                          .values('coal_pref')
                          .order_by()
                          .annotate(players=Count('id')))
        for p in active_players:
            coal[p['coal_pref']] = p['players']
        return coal

    def get_title(self):
        if self.title:
            return self.title
        else:
            from django.template.defaultfilters import date
            return date(self.date_start, 'F Y')

    get_title.allow_tags = True
    get_title.short_description = _('title')

    def days_left(self):
        total_days = self.days_in_tour()
        now = timezone.now()
        if self.date_start.month != now.month:
            return 0
        days_left = total_days - now.day
        if days_left < 0:
            days_left = 0
        return days_left

    def days_passed(self):
        return self.days_in_tour() - self.days_left()

    def days_in_tour(self):
        return monthrange(self.date_start.year, self.date_start.month)[1]


class Mission(models.Model):
    tour = models.ForeignKey(Tour, related_name='missions', on_delete=models.CASCADE)

    name = models.CharField(max_length=256, blank=True, db_index=True)
    path = models.CharField(max_length=256, blank=True)

    date_start = models.DateTimeField(db_index=True)
    date_end = models.DateTimeField()
    duration = models.IntegerField(default=0)
    timestamp = models.IntegerField(unique=True)
    players_total = models.IntegerField(default=0)
    pilots_total = models.IntegerField(default=0)
    gunners_total = models.IntegerField(default=0)

    COALITIONS = (
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )
    winning_coalition = models.IntegerField(choices=COALITIONS, blank=True, null=True)
    WIN_REASONS = (
        ('score', 'score'),
        ('task', 'task'),
    )
    win_reason = models.CharField(choices=WIN_REASONS, max_length=8, blank=True)

    PRESETS = (
        (0, pgettext_lazy('preset', 'custom')),
        (1, pgettext_lazy('preset', 'normal')),
        (2, pgettext_lazy('preset', 'expert')),
    )
    preset = models.IntegerField(default=1, choices=PRESETS)
    settings = ArrayField(models.BooleanField())

    is_correctly_completed = models.BooleanField(default=False)

    # стоимость объектов и т.п. на момент завершения миссии
    score_dict = JSONField(default=dict)

    is_hide = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-id']
        db_table = 'missions'

    def __str__(self):
        return self.name

    def stats_summary_total(self):
        summary_total = {'ak_total': 0, 'gk_total': 0, 'score': 0, 'flight_time': 0}
        _summary_total = (Sortie.objects
                          .filter(mission_id=self.id, is_disco=False)
                          .aggregate(ak_total=Sum('ak_total'), gk_total=Sum('gk_total'),
                                     score=Sum('score'), flight_time=Sum('flight_time')))
        summary_total.update(_summary_total)
        return summary_total

    def stats_summary_coal(self):
        summary_coal = {
            1: {'ak_total': 0, 'gk_total': 0, 'score': 0, 'flight_time': 0},
            2: {'ak_total': 0, 'gk_total': 0, 'score': 0, 'flight_time': 0},
        }
        _summary_coal = (Sortie.objects
                         .filter(mission_id=self.id, is_disco=False)
                         .values('coalition')
                         .order_by()
                         .annotate(ak_total=Sum('ak_total'), gk_total=Sum('gk_total'),
                                   score=Sum('score'), flight_time=Sum('flight_time')))
        for s in _summary_coal:
            summary_coal[s['coalition']].update(s)
        return summary_coal


class Profile(models.Model):
    uuid = models.UUIDField(unique=True, editable=False)
    nickname = models.CharField(max_length=128, db_index=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile',
                                blank=True, null=True, on_delete=models.SET_NULL)
    squad = models.ForeignKey('squads.Squad', related_name='+', blank=True, null=True, on_delete=models.SET_NULL)
    is_hide = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-id']
        db_table = 'profiles'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return self.nickname

    def get_nicknames(self, exclude_current=True):
        nicknames = set(Sortie.objects.filter(profile_id=self.id)
                        .distinct('nickname').values_list('nickname', flat=True).order_by())
        if exclude_current:
            nicknames.discard(self.nickname)
        return nicknames

    def uuid_sha256_hash(self):
        return hashlib.sha256(self.uuid.hex.encode('utf8')).hexdigest()

    def connect_with_user(self, user):
        self.user = user
        if hasattr(user, 'squad_member'):
            self.squad = user.squad_member.squad
        self.save()


class Player(models.Model):
    tour = models.ForeignKey(Tour, related_name='+', on_delete=models.CASCADE)
    PLAYER_TYPES = (
        ('pilot', 'pilot'),
        ('gunner', 'gunner'),
        ('tankman', 'tankman'),
    )
    type = models.CharField(choices=PLAYER_TYPES, max_length=8, default='pilot', db_index=True)
    profile = models.ForeignKey(Profile, related_name='players', on_delete=models.CASCADE)
    squad = models.ForeignKey('stats.Squad', related_name='players', blank=True, null=True, on_delete=models.SET_NULL)

    date_first_sortie = models.DateTimeField(null=True)
    date_last_sortie = models.DateTimeField(null=True)
    date_last_combat = models.DateTimeField(null=True)

    score = models.BigIntegerField(default=0, db_index=True)
    rating = models.BigIntegerField(default=0, db_index=True)
    ratio = models.FloatField(default=1)

    sorties_total = models.IntegerField(default=0)
    sorties_coal = ArrayField(models.IntegerField(default=0), default=default_coal_list)
    sorties_cls = JSONField(default=default_sorties_cls)

    COALITIONS = (
        (Coalition.neutral, pgettext_lazy('coalition', _('neutral'))),
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )

    coal_pref = models.IntegerField(default=Coalition.neutral, choices=COALITIONS)

    # налет в секундах?
    flight_time = models.BigIntegerField(default=0, db_index=True)

    ammo = JSONField(default=default_ammo)
    accuracy = models.FloatField(default=0, db_index=True)

    streak_current = models.IntegerField(default=0, db_index=True)
    streak_max = models.IntegerField(default=0)

    score_streak_current = models.IntegerField(default=0, db_index=True)
    score_streak_max = models.IntegerField(default=0)

    streak_ground_current = models.IntegerField(default=0, db_index=True)
    streak_ground_max = models.IntegerField(default=0)

    sorties_streak_current = models.IntegerField(default=0)
    sorties_streak_max = models.IntegerField(default=0)

    ft_streak_current = models.IntegerField(default=0)
    ft_streak_max = models.IntegerField(default=0)

    sortie_max_ak = models.IntegerField(default=0)
    sortie_max_gk = models.IntegerField(default=0)

    lost_aircraft_current = models.IntegerField(default=0)

    bailout = models.IntegerField(default=0)
    wounded = models.IntegerField(default=0)
    dead = models.IntegerField(default=0)
    captured = models.IntegerField(default=0)
    relive = models.IntegerField(default=0)

    takeoff = models.IntegerField(default=0)
    landed = models.IntegerField(default=0)
    ditched = models.IntegerField(default=0)
    crashed = models.IntegerField(default=0)
    in_flight = models.IntegerField(default=0)
    shotdown = models.IntegerField(default=0)

    respawn = models.IntegerField(default=0)
    disco = models.IntegerField(default=0)

    ak_total = models.IntegerField(default=0, db_index=True)
    ak_assist = models.IntegerField(default=0)
    gk_total = models.IntegerField(default=0, db_index=True)
    fak_total = models.IntegerField(default=0)
    fgk_total = models.IntegerField(default=0)

    killboard_pvp = JSONField(default=dict)
    killboard_pve = JSONField(default=dict)

    ce = models.FloatField(default=0)
    kd = models.FloatField(default=0, db_index=True)
    kl = models.FloatField(default=0)
    ks = models.FloatField(default=0)
    khr = models.FloatField(default=0, db_index=True)
    gkd = models.FloatField(default=0)
    gkl = models.FloatField(default=0)
    gks = models.FloatField(default=0)
    gkhr = models.FloatField(default=0)
    wl = models.FloatField(default=0)
    elo = models.FloatField(default=1000)

    fairplay = models.IntegerField(default=100)
    fairplay_time = models.IntegerField(default=0)

    objects = models.Manager()
    players = PlayerManager()

    class Meta:
        ordering = ['-id']
        db_table = 'players'
        unique_together = (('profile', 'type', 'tour'),)

    def __str__(self):
        return self.profile.nickname

    def save(self, *args, **kwargs):
        self.update_accuracy()
        self.update_analytics()
        self.update_rating()
        self.update_ratio()
        self.update_coal_pref()
        super().save(*args, **kwargs)

    def get_profile_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:pilot', args=[self.profile_id, self.nickname]),
                                            tour_id=self.tour_id)
        return url

    def get_sorties_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:pilot_sorties', args=[self.profile_id, self.nickname]),
                                            tour_id=self.tour_id)
        return url

    def get_vlifes_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:pilot_vlifes', args=[self.profile_id, self.nickname]),
                                            tour_id=self.tour_id)
        return url

    def get_awards_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:pilot_awards', args=[self.profile_id, self.nickname]),
                                            tour_id=self.tour_id)
        return url

    def get_killboard_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:pilot_killboard', args=[self.profile_id, self.nickname]),
                                            tour_id=self.tour_id)
        return url

    def get_position_by_field(self, field='rating'):
        return get_position_by_field(player=self, field=field)

    @property
    def nickname(self):
        return self.profile.nickname

    @property
    def lost_aircraft(self):
        return self.ditched + self.crashed + self.shotdown

    @property
    def not_takeoff(self):
        return self.sorties_total - self.takeoff

    @property
    def flight_time_hours(self):
        return self.flight_time / 3600

    @property
    def rating_format(self):
        if self.rating > 10000:
            return '{}K'.format(self.rating // 1000)
        else:
            return self.rating

    @property
    def ak_total_ai(self):
        aircraft_light = self.killboard_pve.get('aircraft_light', 0)
        aircraft_medium = self.killboard_pve.get('aircraft_medium', 0)
        aircraft_heavy = self.killboard_pve.get('aircraft_heavy', 0)
        aircraft_transport = self.killboard_pve.get('aircraft_transport', 0)
        return aircraft_light + aircraft_medium + aircraft_heavy + aircraft_transport

    def update_accuracy(self):
        if self.ammo['used_cartridges']:
            self.accuracy = round(self.ammo['hit_bullets'] * 100 / self.ammo['used_cartridges'], 1)

    def update_analytics(self):
        self.kd = round(self.ak_total / max(self.relive, 1), 2)
        self.kl = round(self.ak_total / max(self.lost_aircraft, 1), 2)
        self.ks = round(self.ak_total / max(self.sorties_total, 1), 2)
        self.khr = round(self.ak_total / max(self.flight_time_hours, 1), 2)
        self.gkd = round(self.gk_total / max(self.relive, 1), 2)
        self.gkl = round(self.gk_total / max(self.lost_aircraft, 1), 2)
        self.gks = round(self.gk_total / max(self.sorties_total, 1), 2)
        self.gkhr = round(self.gk_total / max(self.flight_time_hours, 1), 2)
        self.wl = round(self.ak_total / max(self.shotdown, 1), 2)
        self.ce = round(self.kl * self.khr / 10, 2)

    def update_rating(self):
        # score per death
        sd = self.score / max(self.relive, 1)
        # score per hour
        shr = self.score / max(self.flight_time_hours, 1)
        # self.rating = int((sd * shr * self.score) / 1000000)
        self.rating = int((sd * shr * self.score) / 1000)

    def update_ratio(self):
        ratio = Sortie.objects.filter(player_id=self.id).aggregate(ratio=Avg('ratio'))['ratio']
        if ratio:
            self.ratio = round(ratio, 2)

    def update_coal_pref(self):
        if self.sorties_total:
            coal_1 = round(self.sorties_coal[1] * 100 / self.sorties_total, 0)
            if coal_1 > 60:
                self.coal_pref = 1
            elif coal_1 < 40:
                self.coal_pref = 2
            else:
                self.coal_pref = 0


class PlayerMission(models.Model):
    profile = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='+', on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, related_name='+', on_delete=models.CASCADE)

    score = models.IntegerField(default=0, db_index=True)
    ratio = models.FloatField(default=1)

    sorties_total = models.IntegerField(default=0)
    sorties_coal = ArrayField(models.IntegerField(default=0), default=default_coal_list)

    COALITIONS = (
        (Coalition.neutral, pgettext_lazy('coalition', _('neutral'))),
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )

    coal_pref = models.IntegerField(default=Coalition.neutral, choices=COALITIONS)

    # налет в секундах?
    flight_time = models.BigIntegerField(default=0, db_index=True)

    ammo = JSONField(default=default_ammo)
    accuracy = models.FloatField(default=0, db_index=True)

    bailout = models.IntegerField(default=0)
    wounded = models.IntegerField(default=0)
    dead = models.IntegerField(default=0)
    captured = models.IntegerField(default=0)
    relive = models.IntegerField(default=0)

    takeoff = models.IntegerField(default=0)
    landed = models.IntegerField(default=0)
    ditched = models.IntegerField(default=0)
    crashed = models.IntegerField(default=0)
    in_flight = models.IntegerField(default=0)
    shotdown = models.IntegerField(default=0)

    respawn = models.IntegerField(default=0)
    disco = models.IntegerField(default=0)

    ak_total = models.IntegerField(default=0, db_index=True)
    ak_assist = models.IntegerField(default=0)
    gk_total = models.IntegerField(default=0, db_index=True)
    fak_total = models.IntegerField(default=0)
    fgk_total = models.IntegerField(default=0)

    killboard_pvp = JSONField(default=dict)
    killboard_pve = JSONField(default=dict)

    ce = models.FloatField(default=0)
    kd = models.FloatField(default=0, db_index=True)
    kl = models.FloatField(default=0)
    ks = models.FloatField(default=0)
    khr = models.FloatField(default=0, db_index=True)
    gkd = models.FloatField(default=0)
    gkl = models.FloatField(default=0)
    gks = models.FloatField(default=0)
    gkhr = models.FloatField(default=0)
    wl = models.FloatField(default=0)

    class Meta:
        ordering = ['-id']
        db_table = 'players_missions'
        unique_together = (('player', 'mission'),)

    def __str__(self):
        return self.profile.nickname

    def save(self, *args, **kwargs):
        self.update_accuracy()
        self.update_analytics()
        self.update_ratio()
        self.update_coal_pref()
        super().save(*args, **kwargs)

    def get_profile_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:pilot', args=[self.profile_id, self.nickname]),
                                            tour_id=self.player.tour_id)
        return url

    @property
    def nickname(self):
        return self.profile.nickname

    @property
    def lost_aircraft(self):
        return self.ditched + self.crashed + self.shotdown

    @property
    def flight_time_hours(self):
        return self.flight_time / 3600

    def update_accuracy(self):
        if self.ammo['used_cartridges']:
            self.accuracy = round(self.ammo['hit_bullets'] * 100 / self.ammo['used_cartridges'], 1)

    def update_analytics(self):
        self.kd = round(self.ak_total / max(self.relive, 1), 2)
        self.kl = round(self.ak_total / max(self.lost_aircraft, 1), 2)
        self.ks = round(self.ak_total / max(self.sorties_total, 1), 2)
        self.khr = round(self.ak_total / max(self.flight_time_hours, 1), 2)
        self.gkd = round(self.gk_total / max(self.relive, 1), 2)
        self.gkl = round(self.gk_total / max(self.lost_aircraft, 1), 2)
        self.gks = round(self.gk_total / max(self.sorties_total, 1), 2)
        self.gkhr = round(self.gk_total / max(self.flight_time_hours, 1), 2)
        self.wl = round(self.ak_total / max(self.shotdown, 1), 2)
        self.ce = round(self.kl * self.khr / 10, 2)

    def update_ratio(self):
        ratio = (Sortie.objects.filter(player_id=self.id, mission_id=self.mission_id)
                 .aggregate(ratio=Avg('ratio'))['ratio'])
        if ratio:
            self.ratio = round(ratio, 2)

    def update_coal_pref(self):
        if self.sorties_total:
            coal_1 = round(self.sorties_coal[1] * 100 / self.sorties_total, 0)
            if coal_1 > 60:
                self.coal_pref = 1
            elif coal_1 < 40:
                self.coal_pref = 2
            else:
                self.coal_pref = 0


class PlayerAircraft(models.Model):
    profile = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='+', on_delete=models.CASCADE)
    aircraft = models.ForeignKey(Object, related_name='+', on_delete=models.PROTECT)

    score = models.IntegerField(default=0)
    ratio = models.FloatField(default=1)

    sorties_total = models.IntegerField(default=0)
    flight_time = models.BigIntegerField(default=0)

    ammo = JSONField(default=default_ammo)
    accuracy = models.FloatField(default=0)

    bailout = models.IntegerField(default=0)
    wounded = models.IntegerField(default=0)
    dead = models.IntegerField(default=0)
    captured = models.IntegerField(default=0)
    relive = models.IntegerField(default=0)

    takeoff = models.IntegerField(default=0)
    landed = models.IntegerField(default=0)
    ditched = models.IntegerField(default=0)
    crashed = models.IntegerField(default=0)
    in_flight = models.IntegerField(default=0)
    shotdown = models.IntegerField(default=0)

    respawn = models.IntegerField(default=0)
    disco = models.IntegerField(default=0)

    ak_total = models.IntegerField(default=0)
    ak_assist = models.IntegerField(default=0)
    gk_total = models.IntegerField(default=0)
    fak_total = models.IntegerField(default=0)
    fgk_total = models.IntegerField(default=0)

    killboard_pvp = JSONField(default=dict)
    killboard_pve = JSONField(default=dict)

    ce = models.FloatField(default=0)
    kd = models.FloatField(default=0)
    kl = models.FloatField(default=0)
    ks = models.FloatField(default=0)
    khr = models.FloatField(default=0)
    gkd = models.FloatField(default=0)
    gkl = models.FloatField(default=0)
    gks = models.FloatField(default=0)
    gkhr = models.FloatField(default=0)
    wl = models.FloatField(default=0)

    class Meta:
        # ordering = ['-id']
        db_table = 'players_aircraft'
        unique_together = (('player', 'aircraft'),)

    def __str__(self):
        return '{nickname} [{aircraft}]'.format(nickname=self.profile.nickname, aircraft=self.aircraft.name)

    @property
    def nickname(self):
        return self.profile.nickname

    @property
    def lost_aircraft(self):
        return self.ditched + self.crashed + self.shotdown

    @property
    def flight_time_hours(self):
        return self.flight_time / 3600

    def save(self, *args, **kwargs):
        self.update_accuracy()
        self.update_analytics()
        self.update_ratio()
        super().save(*args, **kwargs)

    def update_accuracy(self):
        if self.ammo['used_cartridges']:
            self.accuracy = round(self.ammo['hit_bullets'] * 100 / self.ammo['used_cartridges'], 1)

    def update_analytics(self):
        self.kd = round(self.ak_total / max(self.relive, 1), 2)
        self.kl = round(self.ak_total / max(self.lost_aircraft, 1), 2)
        self.ks = round(self.ak_total / max(self.sorties_total, 1), 2)
        self.khr = round(self.ak_total / max(self.flight_time_hours, 1), 2)
        self.gkd = round(self.gk_total / max(self.relive, 1), 2)
        self.gkl = round(self.gk_total / max(self.lost_aircraft, 1), 2)
        self.gks = round(self.gk_total / max(self.sorties_total, 1), 2)
        self.gkhr = round(self.gk_total / max(self.flight_time_hours, 1), 2)
        self.wl = round(self.ak_total / max(self.shotdown, 1), 2)
        self.ce = round(self.kl * self.khr / 10, 2)

    def update_ratio(self):
        ratio = (Sortie.objects.filter(player_id=self.id, aircraft_id=self.aircraft_id)
                 .aggregate(ratio=Avg('ratio'))['ratio'])
        if ratio:
            self.ratio = round(ratio, 2)


class VLife(models.Model):
    profile = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='+', on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, related_name='+', on_delete=models.CASCADE)

    date_first_sortie = models.DateTimeField(null=True)
    date_last_sortie = models.DateTimeField(null=True)
    date_last_combat = models.DateTimeField(null=True)

    score = models.IntegerField(default=0, db_index=True)
    ratio = models.FloatField(default=1)

    sorties_total = models.IntegerField(default=0, db_index=True)
    sorties_coal = ArrayField(models.IntegerField(default=0), default=default_coal_list)
    sorties_cls = JSONField(default=default_sorties_cls)

    COALITIONS = (
        (Coalition.neutral, pgettext_lazy('coalition', _('neutral'))),
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )

    coal_pref = models.IntegerField(default=Coalition.neutral, choices=COALITIONS)

    flight_time = models.BigIntegerField(default=0, db_index=True)

    ammo = JSONField(default=default_ammo)
    accuracy = models.FloatField(default=0, db_index=True)

    bailout = models.IntegerField(default=0)
    wounded = models.IntegerField(default=0)
    dead = models.IntegerField(default=0)
    captured = models.IntegerField(default=0)
    relive = models.IntegerField(default=0, db_index=True)

    takeoff = models.IntegerField(default=0)
    landed = models.IntegerField(default=0)
    ditched = models.IntegerField(default=0)
    crashed = models.IntegerField(default=0)
    in_flight = models.IntegerField(default=0)
    shotdown = models.IntegerField(default=0)

    respawn = models.IntegerField(default=0)
    disco = models.IntegerField(default=0)

    ak_total = models.IntegerField(default=0, db_index=True)
    ak_assist = models.IntegerField(default=0)
    gk_total = models.IntegerField(default=0, db_index=True)
    fak_total = models.IntegerField(default=0)
    fgk_total = models.IntegerField(default=0)

    killboard_pvp = JSONField(default=dict)
    killboard_pve = JSONField(default=dict)

    STATUS = (
        (SortieStatus.landed, pgettext_lazy('sortie_status', 'landed')),
        (SortieStatus.ditched, pgettext_lazy('sortie_status', 'ditched')),
        (SortieStatus.crashed, pgettext_lazy('sortie_status', 'crashed')),
        (SortieStatus.shotdown, pgettext_lazy('sortie_status', 'shotdown')),
        (SortieStatus.not_takeoff, pgettext_lazy('sortie_status', 'not takeoff')),
        (SortieStatus.in_flight, pgettext_lazy('sortie_status', 'in flight')),
    )

    status = models.CharField(max_length=12, choices=STATUS, default=SortieStatus.not_takeoff)

    AIRCRAFT_STATUS = (
        (LifeStatus.unharmed, pgettext_lazy('aircraft_status', 'unharmed')),
        (LifeStatus.damaged, pgettext_lazy('aircraft_status', 'damaged')),
        (LifeStatus.destroyed, pgettext_lazy('aircraft_status', 'destroyed')),
    )

    aircraft_status = models.CharField(max_length=12, choices=AIRCRAFT_STATUS, default=LifeStatus.unharmed)

    BOT_STATUS = (
        (BotLifeStatus.healthy, pgettext_lazy('sortie_status', 'healthy')),
        (BotLifeStatus.wounded, pgettext_lazy('sortie_status', 'wounded')),
        (BotLifeStatus.dead, pgettext_lazy('sortie_status', 'dead')),
    )

    bot_status = models.CharField(max_length=12, choices=BOT_STATUS, default=BotLifeStatus.healthy)

    ce = models.FloatField(default=0)
    kl = models.FloatField(default=0)
    ks = models.FloatField(default=0)
    khr = models.FloatField(default=0)
    gkl = models.FloatField(default=0)
    gks = models.FloatField(default=0)
    gkhr = models.FloatField(default=0)
    wl = models.FloatField(default=0)

    objects = models.Manager()
    players = VLifeManager()

    class Meta:
        ordering = ['-id']
        db_table = 'vlifes'

    def __str__(self):
        return self.profile.nickname

    def save(self, *args, **kwargs):
        self.update_accuracy()
        self.update_analytics()
        self.update_ratio()
        self.update_coal_pref()
        super().save(*args, **kwargs)

    @property
    def is_dead(self):
        return self.bot_status == BotLifeStatus.dead

    @property
    def is_healthy(self):
        return self.bot_status == BotLifeStatus.healthy

    @property
    def is_wounded(self):
        return self.bot_status == BotLifeStatus.wounded

    @property
    def is_not_takeoff(self):
        return self.status == SortieStatus.not_takeoff

    @property
    def is_landed(self):
        return self.status == SortieStatus.landed

    @property
    def is_in_flight(self):
        return self.status == SortieStatus.in_flight

    @property
    def is_ditched(self):
        return self.status == SortieStatus.ditched

    @property
    def is_captured(self):
        return self.captured

    @property
    def is_crashed(self):
        return self.status == SortieStatus.crashed

    @property
    def is_shotdown(self):
        return self.status == SortieStatus.shotdown

    @property
    def is_lost_aircraft(self):
        return self.is_ditched or self.is_crashed or self.is_shotdown

    @property
    def nickname(self):
        return self.profile.nickname

    @property
    def lost_aircraft(self):
        return self.ditched + self.crashed + self.shotdown

    @property
    def flight_time_hours(self):
        return self.flight_time / 3600

    @property
    def ak_total_ai(self):
        aircraft_light = self.killboard_pve.get('aircraft_light', 0)
        aircraft_medium = self.killboard_pve.get('aircraft_medium', 0)
        aircraft_heavy = self.killboard_pve.get('aircraft_heavy', 0)
        aircraft_transport = self.killboard_pve.get('aircraft_transport', 0)
        return aircraft_light + aircraft_medium + aircraft_heavy + aircraft_transport

    def update_accuracy(self):
        if self.ammo['used_cartridges']:
            self.accuracy = round(self.ammo['hit_bullets'] * 100 / self.ammo['used_cartridges'], 1)

    def update_analytics(self):
        self.kl = round(self.ak_total / max(self.lost_aircraft, 1), 2)
        self.ks = round(self.ak_total / max(self.sorties_total, 1), 2)
        self.khr = round(self.ak_total / max(self.flight_time_hours, 1), 2)
        self.gkl = round(self.gk_total / max(self.lost_aircraft, 1), 2)
        self.gks = round(self.gk_total / max(self.sorties_total, 1), 2)
        self.gkhr = round(self.gk_total / max(self.flight_time_hours, 1), 2)
        self.wl = round(self.ak_total / max(self.shotdown, 1), 2)
        self.ce = round(self.kl * self.khr / 10, 2)

    def update_ratio(self):
        ratio = (Sortie.objects.filter(player_id=self.id, vlife_id=self.id)
                 .aggregate(ratio=Avg('ratio'))['ratio'])
        if ratio:
            self.ratio = round(ratio, 2)

    def update_coal_pref(self):
        if self.sorties_total:
            coal_1 = round(self.sorties_coal[1] * 100 / self.sorties_total, 0)
            if coal_1 > 60:
                self.coal_pref = 1
            elif coal_1 < 40:
                self.coal_pref = 2
            else:
                self.coal_pref = 0


class Sortie(models.Model):
    profile = models.ForeignKey(Profile, related_name='+', on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name='sorties_list', on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, related_name='sorties', on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, related_name='sorties_list', on_delete=models.CASCADE)
    vlife = models.ForeignKey(VLife, related_name='sorties_list', on_delete=models.CASCADE, blank=True, null=True)

    nickname = models.CharField(max_length=128)

    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)
    flight_time = models.IntegerField(default=0)

    # parent = models.ForeignKey('self', related_name='children', blank=True, null=True, on_delete=models.PROTECT)

    aircraft = models.ForeignKey(Object, related_name='+', on_delete=models.PROTECT)

    fuel = models.IntegerField(default=100)  # в процентах!
    skin = models.CharField(max_length=256, blank=True)
    payload_id = models.IntegerField(default=0)
    weapon_mods_id = ArrayField(models.IntegerField(), default=list)

    ammo = JSONField(default=default_ammo)

    COALITIONS = (
        (Coalition.neutral, pgettext_lazy('coalition', _('neutral'))),
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )

    COUNTRIES = (
        (Country.neutral, pgettext_lazy('country', _('neutral'))),
        (Country.USSR, pgettext_lazy('country', _('USSR'))),
        (Country.GreatBritain, pgettext_lazy('country', _('Great Britain'))),
        (Country.USA, pgettext_lazy('country', _('USA'))),
        (Country.Germany, pgettext_lazy('country', _('Germany'))),
        (Country.Italy, pgettext_lazy('country', _('Italy'))),
        (Country.Japan, pgettext_lazy('country', _('Japan'))),
        (Country.France, pgettext_lazy('country', _('France'))),
        (Country.GreatBritainWW1, pgettext_lazy('country', _('Great Britain'))),
        (Country.UnitedStatesWW1, pgettext_lazy('country', _('USA'))),
        (Country.Belgium, pgettext_lazy('country', _('Belgium'))),
        (Country.Russia, pgettext_lazy('country', _('Russia'))),
        (Country.GermanyWW1, pgettext_lazy('country', _('Germany'))),
        (Country.AustriaHungary, pgettext_lazy('country', _('Austria-Hungary'))),
    )

    coalition = models.IntegerField(default=Coalition.neutral, choices=COALITIONS)
    country = models.IntegerField(default=Country.neutral, choices=COUNTRIES)

    ak_total = models.IntegerField(default=0)
    ak_assist = models.IntegerField(default=0)
    gk_total = models.IntegerField(default=0)
    fak_total = models.IntegerField(default=0)
    fgk_total = models.IntegerField(default=0)

    killboard_pvp = JSONField(default=dict)
    killboard_pve = JSONField(default=dict)

    STATUS = (
        (SortieStatus.landed, pgettext_lazy('sortie_status', 'landed')),
        (SortieStatus.ditched, pgettext_lazy('sortie_status', 'ditched')),
        (SortieStatus.crashed, pgettext_lazy('sortie_status', 'crashed')),
        (SortieStatus.shotdown, pgettext_lazy('sortie_status', 'shotdown')),
        (SortieStatus.not_takeoff, pgettext_lazy('sortie_status', 'not takeoff')),
        (SortieStatus.in_flight, pgettext_lazy('sortie_status', 'in flight')),
    )

    status = models.CharField(max_length=12, choices=STATUS, default=SortieStatus.not_takeoff)

    AIRCRAFT_STATUS = (
        (LifeStatus.unharmed, pgettext_lazy('aircraft_status', 'unharmed')),
        (LifeStatus.damaged, pgettext_lazy('aircraft_status', 'damaged')),
        (LifeStatus.destroyed, pgettext_lazy('aircraft_status', 'destroyed')),
    )

    aircraft_status = models.CharField(max_length=12, choices=AIRCRAFT_STATUS, default=LifeStatus.unharmed)

    BOT_STATUS = (
        (BotLifeStatus.healthy, pgettext_lazy('sortie_status', 'healthy')),
        (BotLifeStatus.wounded, pgettext_lazy('sortie_status', 'wounded')),
        (BotLifeStatus.dead, pgettext_lazy('sortie_status', 'dead')),
    )

    bot_status = models.CharField(max_length=12, choices=BOT_STATUS, default=BotLifeStatus.healthy)

    is_airstart = models.BooleanField(default=False)
    is_bailout = models.BooleanField(default=False)
    is_captured = models.BooleanField(default=False)
    is_disco = models.BooleanField(default=False)

    ratio = models.FloatField(default=1)
    score = models.IntegerField(default=0)
    score_dict = JSONField(default=dict)
    damage = models.FloatField(default=0)
    wound = models.FloatField(default=0)

    fairplay = models.IntegerField(default=100)
    bonus = JSONField(default=dict)

    debug = JSONField(default=dict)
    is_ignored = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']
        db_table = 'sorties'

    def __str__(self):
        return self.nickname

    @property
    def is_dead(self):
        return self.bot_status == BotLifeStatus.dead

    @property
    def is_healthy(self):
        return self.bot_status == BotLifeStatus.healthy

    @property
    def is_wounded(self):
        return self.bot_status == BotLifeStatus.wounded

    @property
    def is_not_takeoff(self):
        return self.status == SortieStatus.not_takeoff

    @property
    def is_landed(self):
        return self.status == SortieStatus.landed

    @property
    def is_in_flight(self):
        return self.status == SortieStatus.in_flight

    @property
    def is_ditched(self):
        return self.status == SortieStatus.ditched

    @property
    def is_crashed(self):
        return self.status == SortieStatus.crashed

    @property
    def is_shotdown(self):
        return self.status == SortieStatus.shotdown

    @property
    def is_relive(self):
        return self.is_dead or self.is_captured

    @property
    def is_lost_aircraft(self):
        return self.is_ditched or self.is_crashed or self.is_shotdown

    @property
    def accuracy(self):
        if self.ammo['used_cartridges']:
            return round(self.ammo['hit_bullets'] * 100 / self.ammo['used_cartridges'], 1)
        else:
            return 0

    @property
    def ak_total_ai(self):
        aircraft_light = self.killboard_pve.get('aircraft_light', 0)
        aircraft_medium = self.killboard_pve.get('aircraft_medium', 0)
        aircraft_heavy = self.killboard_pve.get('aircraft_heavy', 0)
        aircraft_transport = self.killboard_pve.get('aircraft_transport', 0)
        return aircraft_light + aircraft_medium + aircraft_heavy + aircraft_transport

    @property
    def modifications(self):
        return get_aircraft_mods(aircraft=self.aircraft.log_name, id_list=tuple(self.weapon_mods_id))

    @property
    def payload(self):
        return get_aircraft_payload(aircraft=self.aircraft.log_name, payload_id=self.payload_id)


class KillboardPvP(models.Model):
    player_1 = models.ForeignKey(Player, related_name='+', on_delete=models.CASCADE)
    player_2 = models.ForeignKey(Player, related_name='+', on_delete=models.CASCADE)
    won_1 = models.IntegerField(default=0)
    won_2 = models.IntegerField(default=0)
    wl_1 = models.FloatField(default=0)
    wl_2 = models.FloatField(default=0)

    class Meta:
        db_table = 'killboard_pvp'
        ordering = ['-id']
        unique_together = (('player_1', 'player_2'),)

    def __str__(self):
        return '{} vs {}'.format(self.player_1.profile.nickname, self.player_2.profile.nickname)

    def save(self, *args, **kwargs):
        self.update_analytics()
        super().save(*args, **kwargs)

    def update_analytics(self):
        self.wl_1 = round(self.won_1 / max(self.won_2, 1), 2)
        self.wl_2 = round(self.won_2 / max(self.won_1, 1), 2)

    def add_won(self, player):
        if player.id == self.player_1.id:
            self.won_1 += 1
        else:
            self.won_2 += 1


class LogEntry(models.Model):
    TYPES = (
        ('respawn', 'respawn'),
        ('end', 'end'),

        ('takeoff', 'takeoff'),
        ('landed', 'landed'),
        ('ditched', 'ditched'),
        ('crashed', 'crashed'),
        ('bailout', 'bailout'),

        ('damaged', 'damaged'),
        ('wounded', 'wounded'),
        ('killed', 'killed'),
        ('destroyed', 'destroyed'),
        ('shotdown', 'shotdown'),
    )

    mission = models.ForeignKey(Mission, related_name='+', on_delete=models.CASCADE)
    act_object = models.ForeignKey(Object, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    act_sortie = models.ForeignKey(Sortie, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    cact_object = models.ForeignKey(Object, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    cact_sortie = models.ForeignKey(Sortie, related_name='+', blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField()
    tik = models.IntegerField(db_index=True)
    type = models.CharField(max_length=16, choices=TYPES, db_index=True)
    extra_data = JSONField(default=dict)

    class Meta:
        db_table = 'log_entries'
        ordering = ['-id']

    def __str__(self):
        return 'LogEntry %s' % self.id


class Squad(models.Model):
    tour = models.ForeignKey(Tour, related_name='+', on_delete=models.CASCADE)
    profile = models.ForeignKey('squads.Squad', related_name='stats', on_delete=models.CASCADE)

    num_members = models.PositiveIntegerField(default=0, db_index=True)
    max_members = models.PositiveIntegerField(default=0)

    score = models.BigIntegerField(default=0, db_index=True)
    rating = models.BigIntegerField(default=0, db_index=True)

    sorties_total = models.IntegerField(default=0)
    sorties_coal = ArrayField(models.IntegerField(default=0), default=default_coal_list)
    sorties_cls = JSONField(default=default_sorties_cls)

    COALITIONS = (
        (Coalition.neutral, pgettext_lazy('coalition', _('neutral'))),
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )

    coal_pref = models.IntegerField(default=Coalition.neutral, choices=COALITIONS)

    # налет в секундах?
    flight_time = models.BigIntegerField(default=0, db_index=True)

    bailout = models.IntegerField(default=0)
    wounded = models.IntegerField(default=0)
    dead = models.IntegerField(default=0)
    captured = models.IntegerField(default=0)
    relive = models.IntegerField(default=0)

    takeoff = models.IntegerField(default=0)
    landed = models.IntegerField(default=0)
    ditched = models.IntegerField(default=0)
    crashed = models.IntegerField(default=0)
    in_flight = models.IntegerField(default=0)
    shotdown = models.IntegerField(default=0)

    respawn = models.IntegerField(default=0)
    disco = models.IntegerField(default=0)  # TODO удалить

    ak_total = models.IntegerField(default=0, db_index=True)
    ak_assist = models.IntegerField(default=0)
    gk_total = models.IntegerField(default=0, db_index=True)
    fak_total = models.IntegerField(default=0)
    fgk_total = models.IntegerField(default=0)

    ce = models.FloatField(default=0)
    kd = models.FloatField(default=0, db_index=True)
    kl = models.FloatField(default=0)
    ks = models.FloatField(default=0)
    khr = models.FloatField(default=0, db_index=True)
    gkd = models.FloatField(default=0)
    gkl = models.FloatField(default=0)
    gks = models.FloatField(default=0)
    gkhr = models.FloatField(default=0)
    wl = models.FloatField(default=0)

    objects = models.Manager()
    squads = SquadManager()

    class Meta:
        ordering = ['-id']
        db_table = 'squads_stats'
        unique_together = (('profile', 'tour'),)

    def __str__(self):
        return self.profile.name

    def save(self, *args, **kwargs):
        self.update_num_members()
        self.update_analytics()
        if self.max_members:
            self.update_rating()
        self.update_coal_pref()
        super().save(*args, **kwargs)

    def get_profile_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:squad', args=[self.profile_id, self.tag]),
                                            tour_id=self.tour_id)
        return url

    def get_pilots_url(self):
        url = '{url}?tour={tour_id}'.format(url=reverse('stats:squad_pilots', args=[self.profile_id, self.tag]),
                                            tour_id=self.tour_id)
        return url

    def get_position_by_field(self, field='rating'):
        return get_squad_position_by_field(squad=self, field=field)

    @property
    def name(self):
        return self.profile.name

    @property
    def tag(self):
        return self.profile.tag

    @property
    def lost_aircraft(self):
        return self.ditched + self.crashed + self.shotdown

    @property
    def not_takeoff(self):
        return self.sorties_total - self.takeoff

    @property
    def flight_time_hours(self):
        return self.flight_time / 3600

    @property
    def rating_format(self):
        if self.rating > 10000:
            return '{}K'.format(self.rating // 1000)
        else:
            return self.rating

    @property
    def ak_total_ai(self):
        aircraft_light = self.killboard_pve.get('aircraft_light', 0)
        aircraft_medium = self.killboard_pve.get('aircraft_medium', 0)
        aircraft_heavy = self.killboard_pve.get('aircraft_heavy', 0)
        aircraft_transport = self.killboard_pve.get('aircraft_transport', 0)
        return aircraft_light + aircraft_medium + aircraft_heavy + aircraft_transport

    def update_analytics(self):
        self.kd = round(self.ak_total / max(self.relive, 1), 2)
        self.kl = round(self.ak_total / max(self.lost_aircraft, 1), 2)
        self.ks = round(self.ak_total / max(self.sorties_total, 1), 2)
        self.khr = round(self.ak_total / max(self.flight_time_hours, 1), 2)
        self.gkd = round(self.gk_total / max(self.relive, 1), 2)
        self.gkl = round(self.gk_total / max(self.lost_aircraft, 1), 2)
        self.gks = round(self.gk_total / max(self.sorties_total, 1), 2)
        self.gkhr = round(self.gk_total / max(self.flight_time_hours, 1), 2)
        self.wl = round(self.ak_total / max(self.shotdown, 1), 2)
        self.ce = round(self.kl * self.khr / 10, 2)

    def update_rating(self):
        # score per death
        sd = self.score / max(self.relive, 1)
        # score per hour
        shr = self.score / max(self.flight_time_hours, 1)
        self.rating = int(((sd * shr * self.score) / 1000) / self.max_members)

    def update_coal_pref(self):
        if self.sorties_total:
            coal_1 = round(self.sorties_coal[1] * 100 / self.sorties_total, 0)
            if coal_1 > 60:
                self.coal_pref = 1
            elif coal_1 < 40:
                self.coal_pref = 2
            else:
                self.coal_pref = 0

    def update_num_members(self):
        self.num_members = self.players.filter(type='pilot').count()
        if self.num_members > self.max_members:
            self.max_members = self.num_members


class Award(models.Model):
    AWARD_TYPES = (
        ('tour', pgettext_lazy('award_type', 'tour')),
        ('mission', pgettext_lazy('award_type', 'mission')),
        ('sortie', pgettext_lazy('award_type', 'sortie')),
        ('vlife', pgettext_lazy('award_type', 'vlife')),
    )
    func = models.CharField(_('function name'), max_length=128, unique=True)
    title = models.CharField(_('title'), max_length=256)
    type = models.CharField(_('type'), choices=AWARD_TYPES, max_length=8, default='tour')
    desc = models.TextField(_('description'), blank=True)
    img = models.ImageField(_('image'), upload_to='awards/',
                            help_text=_('Image size should be 180x180'))

    class Meta:
        db_table = 'awards'
        verbose_name = _('award')
        verbose_name_plural = _('awards')

    def __str__(self):
        return self.title


class Reward(models.Model):
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rewards'
        unique_together = (('award', 'player'),)
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')

    def __str__(self):
        return '{player} - {award}'.format(player=self.player, award=self.award)


class PlayerOnline(models.Model):
    uuid = models.UUIDField(primary_key=True)
    nickname = models.CharField(max_length=128)
    COALITIONS = (
        (Coalition.coal_1, settings.COAL_1_NAME),
        (Coalition.coal_2, settings.COAL_2_NAME),
    )
    coalition = models.IntegerField(choices=COALITIONS)
    profile = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'online'
        verbose_name = _('player online')
        verbose_name_plural = _('players online')

    def __str__(self):
        return '{nickname} online'.format(nickname=self.nickname)
