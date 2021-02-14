from collections import defaultdict
from datetime import datetime, timedelta
import operator
from pathlib import Path
from pprint import pprint
import sys
from types import MappingProxyType
from zipfile import ZipFile, ZIP_LZMA

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
import pytz
import time

from core import __version__
from mission_report.statuses import LifeStatus
from mission_report.report import MissionReport
from stats.logger import logger
from stats.models import (Object, Mission, Sortie, Profile, Player, PlayerAircraft, VLife,
                          PlayerMission, KillboardPvP, Tour, LogEntry, Score, Squad)
from stats.online import update_online, cleanup_online
from stats.rewards import reward_sortie, reward_tour, reward_mission, reward_vlife
from users.utils import cleanup_registration

User = get_user_model()

MISSION_REPORT_BACKUP_PATH = settings.MISSION_REPORT_BACKUP_PATH
MISSION_REPORT_BACKUP_DAYS = settings.MISSION_REPORT_BACKUP_DAYS
MISSION_REPORT_DELETE = settings.MISSION_REPORT_DELETE
MISSION_REPORT_PATH = settings.MISSION_REPORT_PATH
NEW_TOUR_BY_MONTH = settings.NEW_TOUR_BY_MONTH
TIME_ZONE = pytz.timezone(settings.MISSION_REPORT_TZ)

WIN_BY_SCORE = settings.WIN_BY_SCORE
WIN_SCORE_MIN = settings.WIN_SCORE_MIN
WIN_SCORE_RATIO = settings.WIN_SCORE_RATIO
SORTIE_MIN_TIME = settings.SORTIE_MIN_TIME


def main():
    logger.info('IL2 stats {stats}, Python {python}, Django {django}'.format(
        stats=__version__, python=sys.version[0:5], django=django.get_version()))

    # TODO переделать на проверку по времени создания файлов
    processed_reports = []

    waiting_new_report = False
    online_timestamp = 0

    while True:
        new_reports = []
        for m_report_file in MISSION_REPORT_PATH.glob('missionReport*[[]0[]].txt'):
            if m_report_file.name not in processed_reports:
                new_reports.append(m_report_file)

        if len(new_reports) > 1:
            waiting_new_report = False
            # обрабатываем все логи кроме последней миссии
            for m_report_file in new_reports[:-1]:
                stats_whore(m_report_file=m_report_file)
                cleanup(m_report_file=m_report_file)
                processed_reports.append(m_report_file.name)
            continue
        elif len(new_reports) == 1:
            m_report_file = new_reports[0]
            m_report_files = collect_mission_reports(m_report_file=m_report_file)
            online_timestamp = update_online(m_report_files=m_report_files, online_timestamp=online_timestamp)
            # если последний файл был создан более 2х минут назад - обрабатываем его
            if time.time() - m_report_files[-1].stat().st_mtime > 120:
                waiting_new_report = False
                stats_whore(m_report_file=m_report_file)
                cleanup(m_report_file=m_report_file)
                processed_reports.append(m_report_file.name)
                continue

        if not waiting_new_report:
            logger.info('waiting new report...')
        waiting_new_report = True

        # удаляем юзеров которые не активировали свои регистрации в течении определенного времени
        cleanup_registration()

        # в идеале новые логи появляются как минимум раз в 30 секунд
        time.sleep(30)


def backup_log(name, lines, date):
    path_dir = MISSION_REPORT_BACKUP_PATH.joinpath(str(date.year), str(date.month), str(date.day))
    if not path_dir.exists():
        path_dir.mkdir(parents=True)
    file_path = path_dir.joinpath(name)
    with file_path.open('w') as f:
        f.writelines(lines)
    with ZipFile('%s.zip' % str(file_path), 'w', compression=ZIP_LZMA) as f:
        f.write(str(file_path), arcname=name)
    file_path.unlink()


def collect_mission_reports(m_report_file):
    """ сортировка файлов лога миссии по порядковому номеру """
    return sorted(MISSION_REPORT_PATH.glob('%s*.txt' % m_report_file.name[:34]),
                  key=lambda x: int(x.stem.split('[')[1][:-1]))


def cleanup(m_report_file=None):
    cleanup_online()

    if m_report_file and MISSION_REPORT_DELETE:
        m_report_files = collect_mission_reports(m_report_file=m_report_file)
        # удаляем файлы репорты данной миссии
        for f in m_report_files:
            f.unlink()

    for f in MISSION_REPORT_BACKUP_PATH.glob('**/*.zip'):
        date_creation = datetime.fromtimestamp(f.stat().st_ctime)
        date_cleanup = datetime.now() - timedelta(days=MISSION_REPORT_BACKUP_DAYS)
        if date_creation < date_cleanup:
            f.unlink()

    def get_dirs(directory):
        dirs = []
        for p in directory.iterdir():
            if p.is_dir():
                dirs.append(p)
                dirs.extend(get_dirs(p))
        return dirs

    for d in get_dirs(directory=MISSION_REPORT_BACKUP_PATH):
        try:
            d.rmdir()
        except OSError:
            pass


@transaction.atomic
def stats_whore(m_report_file):
    """
    :type m_report_file: Path
    """
    mission_timestamp = int(time.mktime(time.strptime(m_report_file.name[14:-8], '%Y-%m-%d_%H-%M-%S')))

    if Mission.objects.filter(timestamp=mission_timestamp).exists():
        logger.info('{mission} - exists in the DB'.format(mission=m_report_file.stem))
        return
    logger.info('{mission} - processing new report'.format(mission=m_report_file.stem))

    m_report_files = collect_mission_reports(m_report_file=m_report_file)

    real_date = TIME_ZONE.localize(datetime.fromtimestamp(mission_timestamp))
    real_date = real_date.astimezone(pytz.UTC)

    objects = MappingProxyType({obj['log_name']: obj for obj in Object.objects.values()})
    # classes = MappingProxyType({obj['cls']: obj['cls_base'] for obj in objects.values()})
    score_dict = MappingProxyType({s.key: s.get_value() for s in Score.objects.all()})

    m_report = MissionReport(objects=objects)
    m_report.processing(files=m_report_files)

    backup_log(name=m_report_file.name, lines=m_report.lines, date=real_date)

    if not m_report.is_correctly_completed:
        logger.info('{mission} - mission has not been completed correctly'.format(mission=m_report_file.stem))

    tour = get_tour(date=real_date)

    mission = Mission.objects.create(
        tour_id=tour.id,
        name=m_report.file_path.replace('\\', '/').split('/')[-1].split('.')[0],
        path=m_report.file_path,
        date_start=real_date,
        date_end=real_date + timedelta(seconds=m_report.tik_last // 50),
        duration=m_report.tik_last // 50,
        timestamp=mission_timestamp,
        preset=m_report.preset_id,
        settings=m_report.settings,
        is_correctly_completed=m_report.is_correctly_completed,
        score_dict=dict(score_dict),
    )
    if m_report.winning_coal_id:
        mission.winning_coalition = m_report.winning_coal_id
        mission.win_reason = 'task'
        mission.save()

    # собираем/создаем профили игроков и сквадов
    profiles, players_pilots, players_gunners, players_tankmans, squads = create_profiles(tour=tour, sorties=m_report.sorties)

    players_aircraft = defaultdict(dict)
    players_mission = {}
    players_killboard = {}

    coalition_score = {1: 0, 2: 0}
    new_sorties = []
    new_sortie_to_cls = {}
    for sortie in m_report.sorties:
        sortie_aircraft_id = objects[sortie.aircraft_name]['id']
        profile = profiles[sortie.account_id]
        if sortie.cls_base == 'aircraft':
            player = players_pilots[sortie.account_id]
        elif sortie.cls == 'aircraft_turret':
            player = players_gunners[sortie.account_id]
        elif sortie.cls in ('tank_light', 'tank_heavy', 'tank_medium', 'tank_turret'):
            player = players_tankmans[sortie.account_id]
        else:
            continue

        squad = squads[profile.squad_id] if profile.squad else None
        player.squad = squad

        new_sortie = create_new_sortie(mission=mission, sortie=sortie, profile=profile, player=player,
                                       sortie_aircraft_id=sortie_aircraft_id)
        new_sortie_to_cls[new_sortie.id] = sortie.cls
        update_fairplay(new_sortie=new_sortie)
        update_bonus_score(new_sortie=new_sortie, cls=sortie.cls)

        # не добавляем очки в сумму если было диско
        if not new_sortie.is_disco:
            coalition_score[new_sortie.coalition] += new_sortie.score

        new_sorties.append(new_sortie)
        # добавляем ссылку на запись в базе к объекту вылета, чтобы использовать в добавлении событий вылета
        sortie.sortie_db = new_sortie

    if not mission.winning_coalition and WIN_BY_SCORE:
        _coalition = sorted(coalition_score.items(), key=operator.itemgetter(1), reverse=True)
        max_coal, max_score = _coalition[0]
        min_coal, min_score = _coalition[1]
        # минимальное кол-во очков = 1
        min_score = min_score or 1
        if max_score >= WIN_SCORE_MIN and max_score / min_score >= WIN_SCORE_RATIO:
            mission.winning_coalition = max_coal
            mission.win_reason = 'score'
            mission.save()

    for new_sortie in new_sorties:
        _player_id = new_sortie.player.id
        _profile_id = new_sortie.profile.id

        player_mission = players_mission.setdefault(
            _player_id,
            PlayerMission.objects.get_or_create(profile_id=_profile_id, player_id=_player_id, mission_id=mission.id)[0]
        )

        player_aircraft = players_aircraft[_player_id].setdefault(
            new_sortie.aircraft.id,
            PlayerAircraft.objects.get_or_create(profile_id=_profile_id, player_id=_player_id, aircraft_id=new_sortie.aircraft.id)[0]
        )

        vlife = VLife.objects.get_or_create(profile_id=_profile_id, player_id=_player_id, tour_id=tour.id, relive=0)[0]

        # если случилась победа по очкам - требуется обновить бонусы
        if mission.win_reason == 'score':
            update_bonus_score(new_sortie=new_sortie, cls=new_sortie_to_cls[new_sortie.id])

        update_sortie(new_sortie=new_sortie, player_mission=player_mission, player_aircraft=player_aircraft, vlife=vlife)
        reward_sortie(sortie=new_sortie)

        vlife.save()
        reward_vlife(vlife)

        new_sortie.vlife_id = vlife.id
        new_sortie.save()

    # ===============================================================================
    mission.players_total = len(profiles)
    mission.pilots_total = len(players_pilots)
    mission.gunners_total = len(players_gunners)
    mission.save()

    for p in profiles.values():
        p.save()

    for p in players_pilots.values():
        p.save()
        reward_tour(player=p)

    for p in players_gunners.values():
        p.save()

    for p in players_tankmans.values():
        p.save()

    for aircrafts in players_aircraft.values():
        for a in aircrafts.values():
            a.save()

    for p in players_mission.values():
        p.save()
        reward_mission(player_mission=p)

    for s in squads.values():
        s.save()

    tour.save()

    for event in m_report.log_entries:
        params = {
            'mission_id': mission.id,
            'date': real_date + timedelta(seconds=event['tik'] // 50),
            'tik': event['tik'],
            'extra_data': {
                'pos': event.get('pos'),
            },
        }
        if event['type'] == 'respawn':
            params['type'] = 'respawn'
            params['act_object_id'] = event['sortie'].sortie_db.aircraft.id
            params['act_sortie_id'] = event['sortie'].sortie_db.id
        elif event['type'] == 'end':
            params['type'] = 'end'
            params['act_object_id'] = event['sortie'].sortie_db.aircraft.id
            params['act_sortie_id'] = event['sortie'].sortie_db.id
        elif event['type'] == 'takeoff':
            params['type'] = 'takeoff'
            params['act_object_id'] = event['aircraft'].sortie.sortie_db.aircraft.id
            params['act_sortie_id'] = event['aircraft'].sortie.sortie_db.id
        elif event['type'] == 'landed':
            params['act_object_id'] = event['aircraft'].sortie.sortie_db.aircraft.id
            params['act_sortie_id'] = event['aircraft'].sortie.sortie_db.id
            if event['is_rtb'] and not event['is_killed']:
                params['type'] = 'landed'
            else:
                if event['status'] == LifeStatus.destroyed:
                    params['type'] = 'crashed'
                else:
                    params['type'] = 'ditched'
        elif event['type'] == 'bailout':
            params['type'] = 'bailout'
            params['act_object_id'] = event['bot'].sortie.sortie_db.aircraft.id
            params['act_sortie_id'] = event['bot'].sortie.sortie_db.id
        elif event['type'] == 'damage':
            params['extra_data']['damage'] = event['damage']
            params['extra_data']['is_friendly_fire'] = event['is_friendly_fire']
            if event['target'].cls_base == 'crew':
                params['type'] = 'wounded'
            else:
                params['type'] = 'damaged'
            if event['attacker']:
                if event['attacker'].sortie:
                    params['act_object_id'] = event['attacker'].sortie.sortie_db.aircraft.id
                    params['act_sortie_id'] = event['attacker'].sortie.sortie_db.id
                else:
                    params['act_object_id'] = objects[event['attacker'].log_name]['id']
            if event['target'].sortie:
                params['cact_object_id'] = event['target'].sortie.sortie_db.aircraft.id
                params['cact_sortie_id'] = event['target'].sortie.sortie_db.id
            else:
                params['cact_object_id'] = objects[event['target'].log_name]['id']
        elif event['type'] == 'kill':
            params['extra_data']['is_friendly_fire'] = event['is_friendly_fire']
            if event['target'].cls_base == 'crew':
                params['type'] = 'killed'
            elif event['target'].cls_base == 'aircraft':
                params['type'] = 'shotdown'
            else:
                params['type'] = 'destroyed'
            if event['attacker']:
                if event['attacker'].sortie:
                    params['act_object_id'] = event['attacker'].sortie.sortie_db.aircraft.id
                    params['act_sortie_id'] = event['attacker'].sortie.sortie_db.id
                else:
                    params['act_object_id'] = objects[event['attacker'].log_name]['id']
            if event['target'].sortie:
                params['cact_object_id'] = event['target'].sortie.sortie_db.aircraft.id
                params['cact_sortie_id'] = event['target'].sortie.sortie_db.id
            else:
                params['cact_object_id'] = objects[event['target'].log_name]['id']

        l = LogEntry.objects.create(**params)
        if l.type == 'shotdown' and l.act_sortie and l.cact_sortie and not l.act_sortie.is_disco and not l.extra_data.get('is_friendly_fire'):
            update_killboard_pvp(player=l.act_sortie.player, opponent=l.cact_sortie.player, players_killboard=players_killboard)

    for p in players_killboard.values():
        p.save()

    logger.info('{mission} - processing finished'.format(mission=m_report_file.stem))


def get_tour(date):
    """
    :type date: datetime
    """
    if NEW_TOUR_BY_MONTH:
        try:
            tour = Tour.objects.get(date_start__year=date.year, date_start__month=date.month, is_ended=False)
        except Tour.DoesNotExist:
            tour = Tour.objects.create(date_start=date)
            logger.info('started a new tour by month')
            Tour.objects.exclude(id=tour.id).filter(is_ended=False).update(is_ended=True, date_end=date)
    else:
        try:
            tour = Tour.objects.get(is_ended=False)
        except Tour.DoesNotExist:
            tour = Tour.objects.create(title='Tour name')
            logger.warning('open tour was not found - started a new tour')
        except Tour.MultipleObjectsReturned:
            logger.error('multiple not ended tours - should be only one')
            input()
            sys.exit()
    return tour


def create_profiles(tour, sorties):
    profiles = {}
    players_pilots = {}
    players_gunners = {}
    players_tankmans = {}
    for s in sorties:
        profile = profiles.setdefault(
            s.account_id, Profile.objects.get_or_create(uuid=s.account_id, defaults={'nickname': s.nickname})[0])
        profile.nickname = s.nickname
        if s.cls_base == 'aircraft':
            players_pilots.setdefault(
                s.account_id, Player.objects.get_or_create(profile_id=profile.id, tour_id=tour.id, type='pilot')[0])
        elif s.cls == 'aircraft_turret':
            players_gunners.setdefault(
                s.account_id, Player.objects.get_or_create(profile_id=profile.id, tour_id=tour.id, type='gunner')[0])
        elif s.cls in ('tank_light', 'tank_heavy', 'tank_medium', 'tank_turret'):
            players_tankmans.setdefault(
                s.account_id, Player.objects.get_or_create(profile_id=profile.id, tour_id=tour.id, type='tankman')[0])

    squads = {}
    for p in profiles.values():
        # если профиль не привязан к юзеру, пробуем найти и привязать
        if not p.user:
            try:
                user = User.objects.get(username=p.nickname, is_active=True)
                if not hasattr(user, 'profile'):
                    p.connect_with_user(user=user)
            except User.DoesNotExist:
                pass
        if p.squad:
            squads.setdefault(p.squad_id, Squad.objects.get_or_create(profile_id=p.squad_id, tour_id=tour.id)[0])

    return profiles, players_pilots, players_gunners, players_tankmans, squads


def create_new_sortie(mission, profile, player, sortie, sortie_aircraft_id):
    sortie_tik_last = sortie.tik_bailout or sortie.tik_landed or sortie.tik_end or sortie.tik_last
    sortie_date_start = mission.date_start + timedelta(seconds=sortie.tik_spawn // 50)
    sortie_date_end = mission.date_start + timedelta(seconds=sortie_tik_last // 50)
    flight_time = round((sortie_tik_last - (sortie.tik_takeoff or sortie.tik_spawn)) / 50, 0)

    is_ignored = False
    # вылет игнорируется если общее время вылета меньше установленного конфигом
    if SORTIE_MIN_TIME:
        if (sortie_tik_last // 50) - (sortie.tik_spawn // 50) < SORTIE_MIN_TIME:
            is_ignored = True

    killboard_pvp = defaultdict(int)
    killboard_pve = defaultdict(int)

    ak_total = 0
    fak_total = 0
    ak_assist = 0
    gk_total = 0
    fgk_total = 0
    score = 0

    for targets in sortie.killboard.values():
        for target in targets:
            is_friendly = sortie.coal_id == target.coal_id

            if not is_friendly:
                score += mission.score_dict[target.cls]
                if target.cls_base == 'aircraft':
                    ak_total += 1
                elif target.cls_base in ('block', 'vehicle', 'tank'):
                    gk_total += 1
                if target.sortie:
                    killboard_pvp[target.cls] += 1
                else:
                    killboard_pve[target.cls] += 1
            else:
                cls_name = 'f_%s' % target.cls
                if target.cls_base == 'aircraft':
                    fak_total += 1
                elif target.cls_base in ('block', 'vehicle', 'tank'):
                    fgk_total += 1
                if target.sortie:
                    killboard_pvp[cls_name] += 1
                else:
                    killboard_pve[cls_name] += 1

    for targets in sortie.assistboard.values():
        for target in targets:
            if target.cls_base == 'aircraft':
                # френдов не считаем
                if sortie.coal_id == target.coal_id:
                    continue
                ak_assist += 1
                score += mission.score_dict['ak_assist']

    new_sortie = Sortie(
        profile=profile,
        player=player,
        tour=mission.tour,
        mission=mission,
        nickname=sortie.nickname,
        date_start=sortie_date_start,
        date_end=sortie_date_end,
        flight_time=flight_time,
        aircraft_id=sortie_aircraft_id,
        fuel=sortie.fuel or 0,
        skin=sortie.skin,
        payload_id=sortie.payload_id,
        weapon_mods_id=sortie.weapon_mods_id,
        ammo={'used_cartridges': sortie.used_cartridges,
              'used_bombs': sortie.used_bombs,
              'used_rockets': sortie.used_rockets,
              'used_shells': sortie.used_shells,
              'hit_bullets': sortie.hit_bullets,
              'hit_bombs': sortie.hit_bombs,
              'hit_rockets': sortie.hit_rockets,
              'hit_shells': sortie.hit_shells},
        coalition=sortie.coal_id,
        country=sortie.country_id,
        is_airstart=sortie.is_airstart,

        ak_total=ak_total,
        gk_total=gk_total,
        fak_total=fak_total,
        fgk_total=fgk_total,
        ak_assist=ak_assist,

        killboard_pvp=killboard_pvp,
        killboard_pve=killboard_pve,

        status=sortie.sortie_status.status,
        aircraft_status=sortie.aircraft_status.status,
        bot_status=sortie.bot_status.status,

        is_bailout=sortie.is_bailout,
        is_captured=sortie.is_captured,
        is_disco=sortie.is_disco,

        score=score,
        score_dict={'basic': score},
        ratio=sortie.ratio,
        damage=round(sortie.aircraft_damage, 2),
        wound=round(sortie.bot_damage, 2),
        debug={'aircraft_id': sortie.aircraft_id, 'bot_id': sortie.bot_id},
        is_ignored=is_ignored,
    )

    return new_sortie


def update_sortie(new_sortie, player_mission, player_aircraft, vlife):
    player = new_sortie.player

    if not player.date_first_sortie:
        player.date_first_sortie = new_sortie.date_start
        player.date_last_combat = new_sortie.date_start
    player.date_last_sortie = new_sortie.date_start

    if not vlife.date_first_sortie:
        vlife.date_first_sortie = new_sortie.date_start
        vlife.date_last_combat = new_sortie.date_start
    vlife.date_last_sortie = new_sortie.date_start

    # если вылет был окончен диско - результаты вылета не добавляться к общему профилю
    if new_sortie.is_disco:
        player.disco += 1
        player_mission.disco += 1
        player_aircraft.disco += 1
        vlife.disco += 1
        return
    # если вылет игнорируется по каким либо причинам
    elif new_sortie.is_ignored:
        return

    # если в вылете было что-то уничтожено - считаем его боевым
    if new_sortie.score:
        player.date_last_combat = new_sortie.date_start
        vlife.date_last_combat = new_sortie.date_start

    vlife.status = new_sortie.status
    vlife.aircraft_status = new_sortie.aircraft_status
    vlife.bot_status = new_sortie.bot_status

    # TODO проверить как это отработает для вылетов стрелков
    if not new_sortie.is_not_takeoff:
        player.sorties_coal[new_sortie.coalition] += 1
        player_mission.sorties_coal[new_sortie.coalition] += 1
        vlife.sorties_coal[new_sortie.coalition] += 1

        if player.squad:
            player.squad.sorties_coal[new_sortie.coalition] += 1

        if new_sortie.aircraft.cls_base == 'aircraft':
            if new_sortie.aircraft.cls in player.sorties_cls:
                player.sorties_cls[new_sortie.aircraft.cls] += 1
            else:
                player.sorties_cls[new_sortie.aircraft.cls] = 1

            if new_sortie.aircraft.cls in vlife.sorties_cls:
                vlife.sorties_cls[new_sortie.aircraft.cls] += 1
            else:
                vlife.sorties_cls[new_sortie.aircraft.cls] = 1

            if player.squad:
                if new_sortie.aircraft.cls in player.squad.sorties_cls:
                    player.squad.sorties_cls[new_sortie.aircraft.cls] += 1
                else:
                    player.squad.sorties_cls[new_sortie.aircraft.cls] = 1

    update_general(player=player, new_sortie=new_sortie)
    update_general(player=player_mission, new_sortie=new_sortie)
    update_general(player=player_aircraft, new_sortie=new_sortie)
    update_general(player=vlife, new_sortie=new_sortie)
    if player.squad:
        update_general(player=player.squad, new_sortie=new_sortie)

    update_ammo(sortie=new_sortie, player=player)
    update_ammo(sortie=new_sortie, player=player_mission)
    update_ammo(sortie=new_sortie, player=player_aircraft)
    update_ammo(sortie=new_sortie, player=vlife)

    update_killboard(player=player, killboard_pvp=new_sortie.killboard_pvp,
                     killboard_pve=new_sortie.killboard_pve)
    update_killboard(player=player_mission, killboard_pvp=new_sortie.killboard_pvp,
                     killboard_pve=new_sortie.killboard_pve)
    update_killboard(player=player_aircraft, killboard_pvp=new_sortie.killboard_pvp,
                     killboard_pve=new_sortie.killboard_pve)
    update_killboard(player=vlife, killboard_pvp=new_sortie.killboard_pvp,
                     killboard_pve=new_sortie.killboard_pve)

    player.streak_current = vlife.ak_total
    player.streak_max = max(player.streak_max, player.streak_current)
    player.streak_ground_current = vlife.gk_total
    player.streak_ground_max = max(player.streak_ground_max, player.streak_ground_current)
    player.score_streak_current = vlife.score
    player.score_streak_current_heavy = vlife.score_heavy
    player.score_streak_current_medium = vlife.score_medium
    player.score_streak_current_light = vlife.score_light
    player.score_streak_max = max(player.score_streak_max, player.score_streak_current)
    player.score_streak_max_heavy = max(player.score_streak_max_heavy, player.score_streak_current_heavy)
    player.score_streak_max_medium = max(player.score_streak_max_medium, player.score_streak_current_medium)
    player.score_streak_max_light = max(player.score_streak_max_light, player.score_streak_current_light)

    player.sorties_streak_current = vlife.sorties_total
    player.sorties_streak_max = max(player.sorties_streak_max, player.sorties_streak_current)
    player.ft_streak_current = vlife.flight_time
    player.ft_streak_max = max(player.ft_streak_max, player.ft_streak_current)

    if new_sortie.is_relive:
        player.streak_current = 0
        player.streak_ground_current = 0
        player.score_streak_current = 0
        player.score_streak_current_heavy = 0
        player.score_streak_current_medium = 0
        player.score_streak_current_light = 0
        player.sorties_streak_current = 0
        player.ft_streak_current = 0
        player.lost_aircraft_current = 0
    else:
        if new_sortie.is_lost_aircraft:
            player.lost_aircraft_current += 1

    player.sortie_max_ak = max(player.sortie_max_ak, new_sortie.ak_total)
    player.sortie_max_gk = max(player.sortie_max_gk, new_sortie.gk_total)

    update_status(new_sortie=new_sortie, player=player)
    update_status(new_sortie=new_sortie, player=player_mission)
    update_status(new_sortie=new_sortie, player=player_aircraft)
    update_status(new_sortie=new_sortie, player=vlife)
    if player.squad:
        update_status(new_sortie=new_sortie, player=player.squad)


def update_general(player, new_sortie):
    flight_time_add = 0
    if not new_sortie.is_not_takeoff:
        player.sorties_total += 1
        flight_time_add = new_sortie.flight_time
    player.flight_time += flight_time_add

    relive_add = 1 if new_sortie.is_relive else 0
    player.relive += relive_add

    player.ak_total += new_sortie.ak_total
    player.fak_total += new_sortie.fak_total
    player.gk_total += new_sortie.gk_total
    player.fgk_total += new_sortie.fgk_total
    player.ak_assist += new_sortie.ak_assist
    player.score += new_sortie.score

    try:
        if new_sortie.aircraft.cls == "aircraft_light":
            player.score_light += new_sortie.score
            player.flight_time_light += flight_time_add
            player.relive_light += relive_add
        elif new_sortie.aircraft.cls == "aircraft_medium":
            player.score_medium += new_sortie.score
            player.flight_time_medium += flight_time_add
            player.relive_medium += relive_add
        elif new_sortie.aircraft.cls == "aircraft_heavy":
            player.score_heavy += new_sortie.score
            player.flight_time_heavy += flight_time_add
            player.relive_heavy += relive_add
    except AttributeError:
        pass # Some player objects have no score or relive attributes for light/medium/heavy aircraft.

def update_ammo(sortie, player):
    # в логах есть баги, по окончание вылета у самолета может быть больше боемкомплекта чем было вначале
    if sortie.ammo['used_cartridges'] >= sortie.ammo['hit_bullets']:
        player.ammo['used_cartridges'] += sortie.ammo['used_cartridges']
        player.ammo['hit_bullets'] += sortie.ammo['hit_bullets']
    if sortie.ammo['used_bombs'] >= sortie.ammo['hit_bombs']:
        player.ammo['used_bombs'] += sortie.ammo['used_bombs']
        player.ammo['hit_bombs'] += sortie.ammo['hit_bombs']
    if sortie.ammo['used_rockets'] >= sortie.ammo['hit_rockets']:
        player.ammo['used_rockets'] += sortie.ammo['used_rockets']
        player.ammo['hit_rockets'] += sortie.ammo['hit_rockets']
    if sortie.ammo['used_shells'] >= sortie.ammo['hit_shells']:
        player.ammo['used_shells'] += sortie.ammo['used_shells']
        player.ammo['hit_shells'] += sortie.ammo['hit_shells']


def update_status(new_sortie, player):
    if not new_sortie.is_not_takeoff:
        player.takeoff += 1
    if new_sortie.is_landed:
        player.landed += 1
    elif new_sortie.is_ditched:
        player.ditched += 1
    elif new_sortie.is_crashed:
        player.crashed += 1
    elif new_sortie.is_shotdown:
        player.shotdown += 1
    elif new_sortie.is_in_flight:
        player.in_flight += 1

    if new_sortie.is_dead:
        player.dead += 1
    elif new_sortie.is_wounded:
        player.wounded += 1

    if new_sortie.is_captured and not new_sortie.is_dead:
        player.captured += 1

    if new_sortie.is_bailout:
        player.bailout += 1


def update_killboard(player, killboard_pvp, killboard_pve):
    for cls, num in killboard_pvp.items():
        player.killboard_pvp.setdefault(cls, 0)
        player.killboard_pvp[cls] += num

    for cls, num in killboard_pve.items():
        player.killboard_pve.setdefault(cls, 0)
        player.killboard_pve[cls] += num


def update_killboard_pvp(player, opponent, players_killboard):
    # ключ это tuple из ID'шников двух игроков - отсортированные в порядке возрастания
    kb_key = tuple(sorted((player.id, opponent.id)))
    player_killboard = players_killboard.setdefault(
        kb_key,
        KillboardPvP.objects.get_or_create(player_1_id=kb_key[0], player_2_id=kb_key[1])[0])
    player_killboard.add_won(player=player)


def update_elo_rating(winner, loser):
    if (winner.shotdown + winner.ak_total) <= 30:
        k_winner = 40
    elif winner.elo >= 2400:
        k_winner = 10
    else:
        k_winner = 20
    e_winner = 1 / (1 + 10 ** ((loser.elo - winner.elo) / 400))
    diff = round(k_winner * (1 - e_winner), 2)
    winner.elo += diff
    loser.elo -= diff


def update_fairplay(new_sortie):
    player = new_sortie.player
    score_dict = new_sortie.mission.score_dict

    if new_sortie.is_disco:
        player.fairplay -= score_dict['fairplay_disco']
    if new_sortie.fak_total:
        player.fairplay -= score_dict['fairplay_fak']
    if new_sortie.fgk_total:
        player.fairplay -= score_dict['fairplay_fgk']

    if player.fairplay < 0:
        player.fairplay = 0

    if new_sortie.is_disco or new_sortie.fak_total or new_sortie.fgk_total:
        player.fairplay_time = 0
    elif player.fairplay < 100:
        player.fairplay_time += new_sortie.flight_time
        fairplay_hours = player.fairplay_time // 3600
        if fairplay_hours > 0:
            player.fairplay += (score_dict['fairplay_up'] * fairplay_hours)
            player.fairplay_time -= 3600 * fairplay_hours

    if player.fairplay > 100:
        player.fairplay = 100

    new_sortie.fairplay = player.fairplay


def update_bonus_score(new_sortie, cls):
    # бонус процент
    bonus_pct = 0
    bonus_dict = {}

    # бонусы получают только "честные" игроки
    if new_sortie.fairplay == 100:
        if new_sortie.is_landed:
            bonus_pct += 25
            bonus_dict['landed'] = 25
        if new_sortie.coalition == new_sortie.mission.winning_coalition:
            bonus_pct += 25
            bonus_dict['winning_coalition'] = 25
    bonus_dict['total'] = bonus_pct

    # ставим базовые очки т.к. функция может вызваться несколько раз
    new_sortie.score = new_sortie.score_dict['basic']

    new_sortie.bonus = bonus_dict
    bonus_score = new_sortie.score * bonus_pct // 100
    new_sortie.score_dict['bonus'] = bonus_score
    new_sortie.score += bonus_score
    penalty_score = new_sortie.score * (100 - new_sortie.fairplay) // 100
    new_sortie.score_dict['penalty'] = penalty_score
    new_sortie.score -= penalty_score
    # new_sortie.save()

    if cls == "aircraft_heavy":
        new_sortie.score_heavy = new_sortie.score
    elif cls == "aircraft_medium":
        new_sortie.score_medium = new_sortie.score
    elif cls == "aircraft_light":
        new_sortie.score_light = new_sortie.score