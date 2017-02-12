from collections import defaultdict
from itertools import count
import logging
import operator

from mission_report.statuses import BotLifeStatus, SortieStatus, LifeStatus
from mission_report.helpers import distance, point_in_polygon, is_pos_correct
from mission_report import parse_mission_log_line


logger = logging.getLogger('mission_report')


class MissionReport:
    """
    :type areas: dict[int, Area]
    :type airfields: dict[int, Airfield]
    :type objects_id_map: dict[int, Object]
    :type sorties_aircraft: dict[int, Sortie]
    :type sorties_bots: dict[int, Sortie]
    :type sorties_accounts: dict[str, Sortie]
    :type sorties: list[Sortie]
    :type active_sorties: dict[int, set[Sortie]]
    :type lost_aircraft: dict[int, Sortie]
    :type lost_bots: dict[int, Sortie]
    """

    def __init__(self, objects):
        """
        :type objects: dict
        """
        self.index = count().__next__

        self.tik_last = 0
        self.countries = None
        self.date_game = None
        self.file_path = None
        self.game_type_id = None
        self.mods = None
        self.preset_id = None
        self.settings = None
        self.areas = {}
        self.airfields = {}
        self.objects = objects
        self.objects_id_map = {}
        self.sorties_aircraft = {}
        self.sorties_bots = {}
        self.sorties_accounts = {}
        self.sorties = []
        self.is_correctly_completed = False
        self.active_sorties = defaultdict(set)
        self.lines = []
        self.winning_coal_id = None
        # self.online_uuid = set()
        self.log_entries = []

        # словари вылетов для которых не нашлось объекта - поздняя инициализация
        self.lost_aircraft = {}
        self.lost_bots = {}

        # порядок важен т.к. позиция в tuple соответствует ID события
        self.events_handlers = (self.event_mission_start, self.event_hit, self.event_damage, self.event_kill,
                                self.event_sortie_end, self.event_takeoff, self.event_landing, self.event_mission_end,
                                self.event_mission_result, self.event_airfield, self.event_player, self.event_group,
                                self.event_game_object, self.event_influence_area, self.event_influence_area_boundary,
                                self.event_log_version, self.event_bot_deinitialization, self.event_pos_changed,
                                self.event_bot_eject_leave, self.event_round_end, self.event_player_connected,
                                self.event_player_disconnected)

    def processing(self, files):
        """
        :type files: list
        """
        # TODO добавить проверку на одинаковые записи подряд
        # TODO можно либо собирать список всех записей, либо использовать очередь
        # TODO https://docs.python.org/3/library/collections.html#deque-objects
        # TODO и собирать только 5-10 последних
        for file_path in files:
            for line in file_path.open():
                # игнорируем "плохие" строки без
                if 'AType' not in line:
                    logger.warning('ignored bad string: [{}]'.format(line))
                    continue
                self.lines.append(line)

                try:
                    data = parse_mission_log_line.parse(line)
                except parse_mission_log_line.UnexpectedATypeWarning:
                    logger.warning('unexpected atype: [{}]'.format(line))
                    continue

                atype_id = data.pop('atype_id')

                if data['tik'] > self.tik_last:
                    self.tik_last = data['tik']

                if 'country_id' in data:
                    data['coal_id'] = self.countries[data['country_id']]

                # обновление последней позиции объектов события
                if 'pos' in data:
                    self.update_last_pos(data=data)

                # обновление ratio во время взлета, посадки, убийства, прыжка, завершения
                if atype_id in (3, 4, 5, 6, 18):
                    self.update_ratio(data=data)

                self.events_handlers[atype_id](**data)

                self.update_last_tik(data=data)

    def logger_event(self, event):
        """
        :type event: dict
        """
        event['tik'] = self.tik_last
        self.log_entries.append(event)

    def add_active_sortie(self, sortie):
        """
        :type sortie: Sortie
        """
        self.active_sorties[sortie.coal_id].add(sortie)

    def rm_active_sortie(self, sortie):
        """
        :type sortie: Sortie
        """
        self.active_sorties[sortie.coal_id].discard(sortie)

    def get_areas(self, exclude_coals=None):
        """
        :type exclude_coals: list|None
        """
        exclude_coals = exclude_coals or []
        return [a for a in self.areas.values() if a.is_enabled and a.boundary and a.coal_id not in exclude_coals]

    def get_airfields(self, include_coals=None):
        """
        :type include_coals: list|None
        """
        include_coals = include_coals or []
        if include_coals:
            return [a for a in self.airfields.values() if a.coal_id in include_coals]
        else:
            return self.airfields.values()

    def get_object(self, object_id, create=True):
        """
        :type object_id: int
        :type create: bool
        :rtype: Object | None

        # бывают ситуации когда событие происходит с объектом который не был объявлен
        # в случаи когда это относиться к игроку - создаем объект сами из данных вылета
        """
        if object_id is None:
            return None
        obj = self.objects_id_map.get(object_id)
        if not obj and create:
            aircraft_sortie = self.sorties_aircraft.get(object_id)
            bot_sortie = self.sorties_bots.get(object_id)
            # если нашли вылет по самолету и у этого вылета нет объекта самолета - создаем его
            if aircraft_sortie and not aircraft_sortie.aircraft:
                obj = Object(mission=self, object_id=object_id, object_name=aircraft_sortie.aircraft_name,
                             country_id=aircraft_sortie.country_id, coal_id=aircraft_sortie.coal_id,
                             parent_id=aircraft_sortie.parent_id)
                aircraft_sortie.aircraft = obj
                self.objects_id_map[object_id] = obj
            elif bot_sortie and not bot_sortie.aircraft:
                if bot_sortie.cls_base == 'aircraft':
                    object_name = 'botpilot'
                elif bot_sortie.cls_base == 'turret':
                    object_name = 'botgunner'
                elif bot_sortie.cls_base == 'tank':
                    object_name = 'botdriver'
                else:
                    raise ValueError('sortie: unknown object')
                obj = Object(mission=self, object_id=object_id, object_name=object_name,
                             country_id=bot_sortie.country_id, coal_id=bot_sortie.coal_id,
                             parent_id=bot_sortie.aircraft_id)
                bot_sortie.bot = obj
                self.objects_id_map[object_id] = obj
        return obj

    def update_last_pos(self, data):
        if is_pos_correct(pos=data['pos']):
            for key in ('attacker_id', 'target_id', 'aircraft_id', 'bot_id', 'object_id'):
                if key in data and data[key]:
                    obj = self.get_object(object_id=data[key], create=False)
                    if obj:
                        obj.update_position(pos=data['pos'])

    def update_last_tik(self, data):
        for key in ('attacker_id', 'target_id', 'aircraft_id', 'bot_id', 'object_id'):
            if key in data and data[key]:
                obj = self.get_object(object_id=data[key], create=False)
                if obj and obj.sortie and obj.sortie.tik_last < data['tik']:
                    obj.sortie.tik_last = data['tik']

    def get_current_ratio(self, sortie_coal_id):
        player_side = len(self.active_sorties[sortie_coal_id])
        enemy_side = 0
        for coal_id, players in self.active_sorties.items():
            if coal_id != sortie_coal_id:
                enemy_side += len(players)
        total = player_side + enemy_side
        if total < 2:
            return 1
        else:
            return round((1 - player_side / total) * 2, 2)

    def update_ratio(self, data):
        for key in ('attacker_id', 'target_id', 'id', 'aircraft_id', 'bot_id', 'object_id'):
            if key in data and data[key]:
                obj = self.get_object(object_id=data[key], create=False)
                if obj and obj.sortie:
                    current_ratio = self.get_current_ratio(sortie_coal_id=obj.sortie.coal_id)
                    obj.sortie.update_ratio(current_ratio=current_ratio)

    def event_mission_start(self, tik, date, file_path, game_type_id, countries, settings, mods, preset_id):
        self.tik_last = tik
        self.date_game = date
        self.file_path = file_path
        self.countries = countries
        self.game_type_id = game_type_id
        self.mods = mods
        self.preset_id = preset_id
        self.settings = settings

    def event_hit(self, tik, ammo, attacker_id, target_id):
        ammo = self.objects[ammo.lower()]['cls']
        attacker = self.get_object(object_id=attacker_id)
        target = self.get_object(object_id=target_id)
        if target:
            target.got_hit(ammo=ammo, attacker=attacker)

    def event_damage(self, tik, damage, attacker_id, target_id, pos):
        attacker = self.get_object(object_id=attacker_id)
        target = self.get_object(object_id=target_id)
        # дамага может не быть из-за бага логов
        if target and damage:
            target.got_damaged(damage=damage, attacker=attacker, pos=pos)

    def event_kill(self, tik, attacker_id, target_id, pos):
        attacker = self.get_object(object_id=attacker_id)
        # потому что в логах так бывает что кто-то умер, а кто не известно :)
        target = self.get_object(object_id=target_id)
        if target:
            target.got_killed(attacker=attacker, pos=pos)
            if target.sortie:
                self.rm_active_sortie(sortie=target.sortie)

    def event_sortie_end(self, tik, aircraft_id, bot_id, cartridges, shells, bombs, rockets, pos):
        sortie = self.sorties_bots.get(bot_id)
        # бывают события дубли - проверяем
        if sortie and not sortie.is_ended:
            sortie.ending(tik=tik, cartridges=cartridges, shells=shells, bombs=bombs, rockets=rockets)
            self.logger_event({'type': 'end', 'sortie': sortie, 'pos': pos})
            self.rm_active_sortie(sortie=sortie)

    def event_takeoff(self, tik, aircraft_id, pos):
        aircraft = self.get_object(object_id=aircraft_id)
        if aircraft:
            aircraft.takeoff(tik=tik)
            if aircraft.sortie:
                self.logger_event({'type': 'takeoff', 'aircraft': aircraft, 'pos': pos})

    def event_landing(self, tik, aircraft_id, pos):
        aircraft = self.get_object(object_id=aircraft_id)
        if aircraft:
            aircraft.landing(tik=tik, pos=pos)
            if aircraft.sortie:
                self.logger_event({'type': 'landed', 'pos': pos, 'aircraft': aircraft, 'is_rtb': aircraft.is_rtb,
                                   'status': aircraft.life_status.status, 'is_killed': aircraft.is_killed})

    def event_mission_end(self, tik):
        self.is_correctly_completed = True

    def event_mission_result(self, tik, object_id, coal_id, task_type_id, success, icon_type_id, pos):
        if task_type_id == 0 and coal_id != 0 and success:
            if not self.winning_coal_id:
                self.winning_coal_id = coal_id

    def event_airfield(self, tik, airfield_id, country_id, coal_id, aircraft_id_list, pos):
        if airfield_id in self.airfields:
            self.airfields[airfield_id].update(country_id=country_id, coal_id=coal_id)
        else:
            airfield = Airfield(airfield_id=airfield_id, country_id=country_id, coal_id=coal_id, pos=pos)
            self.airfields[airfield_id] = airfield

    def event_player(self, tik, aircraft_id, bot_id, account_id, profile_id, name, pos, aircraft_name, country_id,
                     coal_id, airfield_id, airstart, parent_id, payload_id, fuel, skin, weapon_mods_id,
                     cartridges, shells, bombs, rockets, form):
        sortie = Sortie(mission=self, tik=tik, aircraft_id=aircraft_id, bot_id=bot_id, account_id=account_id,
                        profile_id=profile_id, name=name, pos=pos, aircraft_name=aircraft_name, country_id=country_id,
                        coal_id=coal_id, airfield_id=airfield_id, airstart=airstart, parent_id=parent_id,
                        payload_id=payload_id, fuel=fuel, skin=skin, weapon_mods_id=weapon_mods_id,
                        cartridges=cartridges, shells=shells, bombs=bombs, rockets=rockets)

        self.add_active_sortie(sortie=sortie)
        self.sorties.append(sortie)
        self.sorties_aircraft[sortie.aircraft_id] = sortie
        self.sorties_bots[sortie.bot_id] = sortie
        self.sorties_accounts[sortie.account_id] = sortie

        current_ratio = self.get_current_ratio(sortie_coal_id=sortie.coal_id)
        sortie.update_ratio(current_ratio=current_ratio)
        self.logger_event({'type': 'respawn', 'sortie': sortie, 'pos': pos})

    def event_group(self, tik, group_id, members_id, leader_id):
        pass

    def event_game_object(self, tik, object_id, object_name, country_id, coal_id, name, parent_id):
        obj = Object(mission=self, object_id=object_id, object_name=object_name,
                     country_id=country_id, coal_id=coal_id, parent_id=parent_id)
        self.objects_id_map[object_id] = obj

    def event_influence_area(self, tik, area_id, country_id, coal_id, enabled, in_air):
        if area_id in self.areas:
            self.areas[area_id].update(country_id=country_id, coal_id=coal_id, enabled=enabled, in_air=in_air)
        else:
            area = Area(area_id=area_id, country_id=country_id, coal_id=coal_id, enabled=enabled, in_air=in_air)
            self.areas[area_id] = area

    def event_influence_area_boundary(self, tik, area_id, boundary):
        self.areas[area_id].boundary = boundary

    def event_log_version(self, tik, version):
        pass

    def event_bot_deinitialization(self, tik, bot_id, pos):
        bot = self.get_object(object_id=bot_id)
        if bot:
            bot.deinitialization()
            if bot.sortie:
                self.rm_active_sortie(sortie=bot.sortie)

    def event_pos_changed(self, tik, object_id, pos):
        pass

    def event_bot_eject_leave(self, tik, bot_id, parent_id, pos):
        bot = self.get_object(object_id=bot_id)
        if bot:
            bot.bot_eject_leave(tik=tik, pos=pos)
            if bot.sortie:
                self.rm_active_sortie(sortie=bot.sortie)
                self.logger_event({'type': 'bailout', 'bot': bot, 'pos': pos})

    def event_round_end(self, tik):
        pass

    def event_player_connected(self, tik, account_id, profile_id):
        # self.online_uuid.add(account_id)
        pass

    def event_player_disconnected(self, tik, account_id, profile_id):
        # self.online_uuid.discard(account_id)
        sortie = self.sorties_accounts.get(account_id)
        # TODO работает только в Ил2, в РОФ нет такого события
        if sortie:
            # вылет был завершен, был прыжок, не был создан самолет, самолет на земле
            if not (sortie.is_ended or sortie.is_bailout or (not sortie.aircraft) or sortie.aircraft.on_ground):
                sortie.is_disco = True


class Area:
    def __init__(self, area_id, country_id, coal_id, enabled, in_air):
        self.id = area_id
        self.country_id = country_id
        self.coal_id = coal_id
        self.is_enabled = enabled
        self.in_air = in_air
        self.boundary = None

    def is_inside(self, pos):
        if self.boundary and is_pos_correct(pos=pos):
            return point_in_polygon(point=pos, polygon=self.boundary)
        else:
            return False

    def update(self, country_id, coal_id, enabled, in_air):
        self.country_id = country_id
        self.coal_id = coal_id
        self.is_enabled = enabled
        self.in_air = in_air


class Airfield:
    def __init__(self, airfield_id, country_id, coal_id, pos):
        self.id = airfield_id
        self.country_id = country_id
        self.coal_id = coal_id
        self.pos = pos

    def on_airfield(self, pos):
        if is_pos_correct(pos=self.pos) and is_pos_correct(pos=pos):
            return distance(self.pos, pos) <= 4000
        else:
            return False

    def update(self, country_id, coal_id):
        self.country_id = country_id
        self.coal_id = coal_id


class Object:
    """
    :type mission: MissionReport
    :type sortie: Sortie | None
    :type parent: Object | None
    :type children: dict[int, Object]
    """
    def __init__(self, mission, object_id, object_name, country_id, coal_id, parent_id):
        self.index = mission.index()
        self.mission = mission
        self.id = object_id
        self.log_name = object_name.lower()
        obj = mission.objects[self.log_name]
        self.cls = obj['cls']
        self.cls_base = obj['cls_base']
        self.country_id = country_id
        self.coal_id = coal_id
        self.parent_id = parent_id
        self.parent = None
        self.bot = None  # для пилотов
        # пилоты, стрелки, турели т.п.
        # словарь чтобы избежать связей с забаговаными объектами т.к. новый нормальный объект заменит багованый
        self.children = {}
        if self.parent_id:
            self.set_parent(self.parent_id)

        self.sortie = None
        # бывают ситуации когда в логах запаздывает инициализация объектов связанных с игроком
        # для таких объектов нужно найти вылет
        if obj['is_playable']:
            if self.cls_base in ('aircraft', 'turret', 'tank'):
                sortie = mission.lost_aircraft.pop(self.id, None)
                if sortie:
                    sortie.aircraft = self
                    self.update_by_sortie(sortie=sortie, is_aircraft=True)
            elif self.cls_base == 'crew':
                sortie = mission.lost_bots.pop(self.id, None)
                if sortie:
                    sortie.bot = self
                    self.update_by_sortie(sortie=sortie, is_aircraft=False)

        self.last_pos = None

        if self.cls_base == 'crew':
            self.life_status = BotLifeStatus()
        else:
            self.life_status = LifeStatus()

        self.is_deinitialized = False

        self.is_takeoff = False
        self.is_killed = False
        self.is_bailout = False
        self.is_captured = False
        self.is_rtb = False  # return to base
        self.on_ground = True
        self.damage = 0.0
        self.damagers = defaultdict(int)
        self.killers = []
        self.killboard = defaultdict(set)
        self.assistboard = defaultdict(set)

    def __hash__(self):
        return self.index

    def set_parent(self, parent_id):
        """
        :type parent_id: int
        """
        self.parent = self.mission.get_object(object_id=parent_id)
        if self.parent:
            if self.cls_base == 'crew':
                self.parent.bot = self
            self.parent_id = parent_id
            self.parent.children[self.id] = self

    def captured(self):
        self.is_captured = True
        for ch in self.children.values():
            if not ch.is_bailout:
                ch.is_captured = True

    def uncaptured(self):
        self.is_captured = False
        for ch in self.children.values():
            if not ch.is_bailout:
                ch.is_captured = False

    def deinitialization(self):
        if self.is_deinitialized:
            return
        self.is_deinitialized = True
        if self.parent:
            self.parent.killed_by_damage()
        # TODO не удаляем объект потому что в логах события могут быть и после
        # https://gist.github.com/vaal-/5ea34735d7aa9f561c23
        # удаляем объект
        # self.mission.objects_id_map.pop(self.id, None)
        # if self.cls_base == 'crew' and self.parent:
        #     self.mission.objects_id_map.pop(self.parent.id, None)

    def takeoff(self, tik):
        self.is_takeoff = True
        self.on_ground = False
        self.is_rtb = False
        self.uncaptured()
        if self.sortie:
            self.sortie.tik_landed = None
            if not self.sortie.tik_takeoff:
                self.sortie.tik_takeoff = tik

    def landing(self, tik, pos):
        self.is_takeoff = True
        self.on_ground = True
        if self.sortie:
            self.sortie.tik_landed = tik
        if self.is_on_enemy_territory(pos=pos):
            self.captured()
        if self.is_aircraft_rtb(pos=pos):
            self.is_rtb = True
        self.killed_by_damage()

    def bot_eject_leave(self, tik, pos):
        self.is_bailout = True
        if self.is_on_enemy_territory(pos=pos):
            self.captured()
        if self.sortie:
            self.sortie.tik_bailout = tik
        if self.parent:
            self.parent.is_bailout = True
            self.parent.is_takeoff = True
            self.parent.life_status.destroy()
            self.parent.killed_by_damage()

    def got_hit(self, ammo, attacker=None):
        """
        :type ammo: str
        :type attacker: Object | None
        """
        # TODO добавить логирование попаданий из пистолета/ракетницы ?
        if attacker and attacker.coal_id != self.coal_id:
            if attacker.sortie:
                if ammo == 'bullet':
                    attacker.sortie.hit_bullets += 1
                elif ammo == 'bomb':
                    attacker.sortie.hit_bombs += 1
                elif ammo == 'rocket':
                    attacker.sortie.hit_rockets += 1
                elif ammo == 'shell':
                    attacker.sortie.hit_shells += 1
            # попадания со стрелка(который и пилот) передаются самолету т.к. боезапас самолета общий
            elif attacker.parent and attacker.parent.sortie:
                if ammo == 'bullet':
                    attacker.parent.sortie.hit_bullets += 1
                elif ammo == 'bomb':
                    attacker.parent.sortie.hit_bombs += 1
                elif ammo == 'rocket':
                    attacker.parent.sortie.hit_rockets += 1
                elif ammo == 'shell':
                    attacker.parent.sortie.hit_shells += 1

    def got_damaged(self, damage, attacker=None, pos=None):
        """
        :type damage: int | float
        :type attacker: Object | None
        """
        if not self.life_status.is_destroyed:
            self.life_status.damage()
            self.damage += damage
            # если атакуем сами себя - убираем прямое упоминание об этом
            if self.is_attack_itself(attacker=attacker):
                attacker = None
            if attacker:
                self.damagers[attacker] += damage
            is_friendly_fire = True if attacker and attacker.coal_id == self.coal_id else False
            self.mission.logger_event({'type': 'damage', 'damage': damage, 'pos': pos, 'attacker': attacker,
                                       'target': self, 'is_friendly_fire': is_friendly_fire})

    def got_killed(self, attacker=None, pos=None, force_by_dmg=False):
        """
        :type attacker: Object | None
        """
        if self.is_killed:
            # TODO добавить логирование
            return

        self.life_status.destroy()
        # дамагеры отсортированные по величине дамага
        damagers = [a[0] for a in sorted(self.damagers.items(), key=operator.itemgetter(1), reverse=True)]
        if attacker:
            if attacker in damagers:
                damagers.remove(attacker)
                damagers.insert(0, attacker)
        # если убийца не известен - вычисляем убийцу по повреждениям
        else:
            # если атакующий не известен и цель самолет в полете -
            # откладываем принятие решения на потом (земля, прыжок и т.п.)
            if not force_by_dmg and (self.cls_base == 'aircraft' and not self.on_ground):
                return
            if damagers:
                attacker = damagers[0]

        # если атакуем сами себя - убираем прямое упоминание об этом
        if self.is_attack_itself(attacker=attacker):
            attacker = None

        is_friendly_fire = True if attacker and attacker.coal_id == self.coal_id else False

        if attacker:
            self.is_killed = True
            self.killers = damagers
            attacker.killboard[self.cls].add(self)
            # добавляем второго по величине дамага в ассисты (если надамагал больше 1%)
            if len(damagers) > 1 and self.damagers[damagers[1]] > 1:
                damagers[1].assistboard[self.cls].add(self)
            # зачет киллов от турелей и т.п.
            # не передавать киллы пилоту, если за стрелка был игрок и был убит союзный объект
            if attacker.parent and not (attacker.sortie and is_friendly_fire):
                    attacker.parent.killboard[self.cls].add(self)
        # если есть убийца, или это игровое событие - пишем в лог
        if attacker or not force_by_dmg:
            self.mission.logger_event({'type': 'kill', 'attacker': attacker, 'pos': pos,
                                       'target': self, 'is_friendly_fire': is_friendly_fire})

    def killed_by_damage(self):
        if not self.is_killed and (self.life_status.is_destroyed or self.is_captured):
            # если самолет приземлился не в зоне своего филда или пилот выпрыгнул или пилот мертв
            # - записываем его как сбитый
            if (self.on_ground and not self.is_rtb) or self.is_bailout or (self.bot and self.bot.life_status.is_destroyed):
                self.got_killed(force_by_dmg=True)

    def update_by_sortie(self, sortie, is_aircraft=True):
        """
        :type sortie: Sortie
        :type is_aircraft: bool
        """
        if is_aircraft:
            if sortie.is_airstart:
                self.on_ground = False
                self.is_takeoff = True
        self.sortie = sortie
        if not self.parent:
            self.set_parent(sortie.parent_id)

    def update_position(self, pos):
        self.last_pos = pos

    def is_aircraft_rtb(self, pos):
        for af in self.mission.get_airfields(include_coals=[self.coal_id]):
            if af.on_airfield(pos=pos):
                return True
        return False

    def is_on_enemy_territory(self, pos):
        for area in self.mission.get_areas(exclude_coals=[0, self.coal_id]):
            if area.is_inside(pos=pos):
                return True
        return False

    def is_attack_itself(self, attacker):
        if attacker:
            if attacker == self or attacker.bot == self:
                return True
            if attacker.sortie and self.sortie and attacker.sortie == self.sortie:
                return True
        return False


class Sortie:
    """
    :type aircraft: Object | None
    :type bot: Object | None
    :type mission: MissionReport
    """
    def __init__(self, mission, tik, aircraft_id, bot_id, account_id, profile_id, name, pos, aircraft_name, country_id,
                 coal_id, airfield_id, airstart, parent_id, payload_id, fuel, skin, weapon_mods_id,
                 cartridges, shells, bombs, rockets):
        self.index = mission.index()

        self.mission = mission
        self.aircraft_id = aircraft_id
        self.bot_id = bot_id
        self.aircraft = None
        self.bot = None

        self.pos_start = pos
        self.account_id = account_id
        self.profile_id = profile_id
        self.nickname = name
        self.aircraft_name = aircraft_name.lower()
        obj = mission.objects[self.aircraft_name]
        self.cls = obj['cls']
        self.cls_base = obj['cls_base']
        if not obj['is_playable']:
            raise ValueError('sortie: unplayable object')
        self.country_id = country_id
        self.coal_id = coal_id
        self.airfield_id = airfield_id
        self.is_airstart = airstart
        self.parent_id = parent_id
        self.parent = mission.sorties_aircraft.get(parent_id)
        self.payload_id = payload_id
        self.fuel = fuel
        self.skin = skin
        self.weapon_mods_id = weapon_mods_id

        self.tik_spawn = tik
        self.tik_takeoff = None
        self.tik_bailout = None
        self.tik_landed = None
        self.tik_end = None
        self.tik_last = tik
        if self.is_airstart:
            self.tik_takeoff = self.tik_spawn

        self.used_cartridges = cartridges
        self.used_shells = shells
        self.used_bombs = bombs
        self.used_rockets = rockets
        self.hit_bullets = 0
        self.hit_bombs = 0
        self.hit_rockets = 0
        self.hit_shells = 0

        self._ratio_list = []
        self.ratio = 1

        # вылет завершен
        self.is_disco = False
        self.is_ended = False

        # логи могут баговать и идти не по порядку
        aircraft = mission.get_object(object_id=self.aircraft_id, create=False)
        # самолет должен быть без вылета
        if aircraft:
            if aircraft.sortie:
                # данный объект самолет уже привязан к другому вылету
                logger.warning('tik: {} - aircraft is already linked to a different sortie'.format(tik))
            else:
                if aircraft.log_name == self.aircraft_name:
                    self.aircraft = aircraft
                    self.aircraft.update_by_sortie(sortie=self, is_aircraft=True)
                else:
                    # вместо самолета/турели какой то другой объект - бомба например
                    logger.warning('tik: {} - it\'s not a aircraft and not the turret'.format(tik))
                    self.mission.objects_id_map.pop(self.aircraft_id, None)
        else:
            # игрок был заспаунен раньше чем его самолет
            logger.warning('tik: {} - respawn before than aircraft initialization'.format(tik))
        if not self.aircraft:
            # добавляем в потеряшки и проверим этот список при будущей инициализации объекта
            mission.lost_aircraft[self.aircraft_id] = self

        bot = mission.get_object(object_id=self.bot_id, create=False)
        # бот должен быть без вылета
        if bot:
            if bot.sortie:
                # данный бот уже привязан к другому вылету
                logger.warning('tik: {} - bot is already linked to a different sortie'.format(tik))
            else:
                if bot.cls_base == 'crew':
                    self.bot = bot
                    self.bot.update_by_sortie(sortie=self, is_aircraft=False)
                else:
                    # вместо бота в самолет/турель "посадили" например бомбу или другой самолет
                    # этот объект удаляется и будет создан заново с установками по умолчанию
                    logger.warning('tik: {} - instead of a bot in an aircraft is not a living entity'.format(tik))
                    mission.objects_id_map.pop(self.bot_id, None)
        else:
            # игрок был заспаунен раньше чем его бот
            logger.warning('tik: {} - respawn before than bot initialization'.format(tik))
        if not self.bot:
            # добавляем в потеряшки и проверим этот список при будущей инициализации объекта
            mission.lost_bots[self.bot_id] = self

    def __hash__(self):
        return self.index

    def ending(self, tik, cartridges, shells, bombs, rockets):
        if self.is_ended:
            return
        self.is_ended = True
        self.tik_end = tik
        self.used_cartridges -= cartridges
        self.used_shells -= shells
        self.used_bombs -= bombs
        self.used_rockets -= rockets

        # если это был вылет игрока-стрелка - то вычитаем его расход бз из расхода бз игрока-пилота
        if self.parent:
            self.parent.used_cartridges -= self.used_cartridges
            self.parent.used_shells -= self.used_shells
            self.parent.used_bombs -= self.used_bombs
            self.parent.used_rockets -= self.used_rockets

        # TODO не удаляем объект потому что в логах события могут быть и после
        # https://gist.github.com/vaal-/5ea34735d7aa9f561c23
        # if self.aircraft:
        #     self.aircraft.deinitialization()
        # if self.bot:
        #     self.bot.deinitialization()

    @property
    def is_bailout(self):
        return self.bot.is_bailout if self.bot else False

    @property
    def is_captured(self):
        return self.bot.is_captured if self.bot else False

    @property
    def killboard(self):
        return self.aircraft.killboard if self.aircraft else {}

    @property
    def assistboard(self):
        return self.aircraft.assistboard if self.aircraft else {}

    @property
    def aircraft_damage(self):
        return self.aircraft.damage if self.aircraft else 0

    @property
    def bot_damage(self):
        return self.bot.damage if self.bot else 0

    @property
    def sortie_status(self):
        """
        :rtype: SortieStatus
        """
        # TODO переписать
        status = SortieStatus()
        if self.aircraft:
            if self.aircraft.is_takeoff:
                status.takeoff()
                if self.aircraft.on_ground:
                    if self.aircraft.is_rtb:
                        status.landing()
                    else:
                        if self.aircraft.life_status.is_destroyed:
                            status.crash()
                        else:
                            status.ditch()
            if self.aircraft.killers:
                status.down()
        if self.bot:
            if self.bot.life_status.is_destroyed or self.bot.is_bailout:
                status.crash()
        return status

    @property
    def aircraft_status(self):
        return self.aircraft.life_status if self.aircraft else LifeStatus()

    @property
    def bot_status(self):
        return self.bot.life_status if self.bot else BotLifeStatus()

    def update_ratio(self, current_ratio):
        self._ratio_list.append(current_ratio)
        self.ratio = round((sum(self._ratio_list) / len(self._ratio_list)), 2)
