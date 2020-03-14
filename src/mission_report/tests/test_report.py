from ..statuses import SortieStatus, BotLifeStatus
from ..report import Airfield, Area, MissionReport, Object, Sortie


def test_airfield(mission):
    """
    :type mission: MissionReport
    """
    airfield = Airfield(airfield_id=10001, country_id=101, coal_id=1,
                        pos={'x': 7500.0, 'y': 0.0, 'z': 7500.0})
    assert airfield.id == 10001
    assert airfield.coal_id == 1
    assert airfield.country_id == 101
    assert airfield.pos == {'x': 7500.0, 'y': 0.0, 'z': 7500.0}

    airfield.update(country_id=201, coal_id=2)
    assert airfield.coal_id == 2
    assert airfield.country_id == 201

    # самолет на филде
    assert airfield.on_airfield(pos={'x': 8000.0, 'y': 0.0, 'z': 8000.0})
    # самолет не на филде
    assert not airfield.on_airfield(pos={'x': 2000.0, 'y': 0.0, 'z': 2000.0})


def test_area(mission):
    """
    :type mission: MissionReport
    """
    area = Area(area_id=10001, country_id=101, coal_id=1, enabled=True, in_air=[0, 0, 0, 0, 0, 0, 0, 0])
    assert area.id == 10001
    assert area.coal_id == 1
    assert area.country_id == 101
    assert area.is_enabled
    assert area.in_air == [0, 0, 0, 0, 0, 0, 0, 0]
    assert area.boundary is None

    area.update(country_id=201, coal_id=2, enabled=False, in_air=[1, 0, 0, 0, 0, 0, 0, 0])
    assert area.coal_id == 2
    assert area.country_id == 201
    assert not area.is_enabled
    assert area.in_air == [1, 0, 0, 0, 0, 0, 0, 0]

    area.boundary = [[0, 0], [15000, 0], [15000, 15000], [0, 15000]]
    assert area.is_inside(pos={'x': 7500.0, 'y': 0.0, 'z': 7500.0})
    assert not area.is_inside(pos={'x': 17500.0, 'y': 0.0, 'z': 17500.0})


def test_sortie(mission):
    """
    :type mission: MissionReport
    """
    data = {
        'aircraft_id': 10011,
        'bot_id': 10012,
        'pos': {'x': 7500.0, 'y': 0.0, 'z': 7500.0},
        'account_id': '76638c27-16d7-4ee2-95be-d326a9c499b7',
        'profile_id': '8d8a0ac5-095d-41ea-93b5-09599a5fde4c',
        'name': 'John Doe',
        'aircraft_name': 'La-5 ser.8',
        'country_id': 101,
        'coal_id': 1,
        'airfield_id': None,
        'airstart': False,
        'parent_id': None,
        'payload_id': 1,
        'fuel': 50,
        'skin': '',
        'weapon_mods_id': [],
        'tik': 20,
        'cartridges': 500,
        'shells': 100,
        'bombs': 2,
        'rockets': 6,
    }
    sortie = Sortie(mission=mission, **data)
    assert sortie.index == 0
    assert sortie.mission == mission
    assert sortie.aircraft_id == data['aircraft_id']
    assert sortie.bot_id == data['bot_id']
    assert sortie.aircraft is None
    assert sortie.bot is None

    assert sortie.pos_start == data['pos']
    assert sortie.account_id == data['account_id']
    assert sortie.profile_id == data['profile_id']
    assert sortie.nickname == data['name']
    assert sortie.aircraft_name == data['aircraft_name'].lower()
    assert sortie.cls == 'aircraft_light'
    assert sortie.cls_base == 'aircraft'

    assert sortie.country_id == data['country_id']
    assert sortie.coal_id == 1
    assert sortie.airfield_id == data['airfield_id']
    assert sortie.is_airstart == data['airstart']
    assert sortie.parent_id == data['parent_id']
    assert sortie.payload_id == data['payload_id']
    assert sortie.fuel == data['fuel']
    assert sortie.skin == data['skin']
    assert sortie.weapon_mods_id == data['weapon_mods_id']

    assert sortie.tik_spawn == data['tik']
    assert sortie.tik_takeoff is None
    assert sortie.tik_landed is None
    assert sortie.tik_end is None
    assert sortie.tik_last == data['tik']

    assert sortie.used_cartridges == data['cartridges']
    assert sortie.used_shells == data['shells']
    assert sortie.used_bombs == data['bombs']
    assert sortie.used_rockets == data['rockets']
    assert sortie.hit_bullets == 0
    assert sortie.hit_bombs == 0
    assert sortie.hit_rockets == 0
    assert sortie.hit_shells == 0

    assert sortie.ratio == 1
    assert sortie.is_disco is False
    assert sortie.is_ended is False

    assert mission.lost_aircraft[data['aircraft_id']] == sortie
    assert mission.lost_bots[data['bot_id']] == sortie

    # assert sortie in mission.active_sorties[sortie.coal_id]
    # assert sortie in mission.sorties
    # assert mission.sorties_aircraft[sortie.aircraft_id] == sortie
    # assert mission.sorties_bots[sortie.bot_id] == sortie
    # assert mission.sorties_accounts[sortie.account_id] == sortie

    sortie.update_ratio(current_ratio=1.2)
    sortie.update_ratio(current_ratio=1)
    assert sortie.ratio == 1.1

    sortie.ending(tik=1000, cartridges=100, shells=75, bombs=1, rockets=4)
    assert sortie.is_ended
    assert sortie.tik_end == 1000
    assert sortie.used_cartridges == 400
    assert sortie.used_bombs == 1
    assert sortie.used_shells == 25
    assert sortie.used_rockets == 2
    # assert sortie not in mission.active_sorties[sortie.coal_id]

    sortie.ending(tik=1200, cartridges=100, shells=75, bombs=1, rockets=4)
    assert sortie.tik_end == 1000

    assert sortie.is_bailout is False
    assert sortie.is_captured is False
    assert sortie.killboard == {}
    assert sortie.assistboard == {}
    assert sortie.aircraft_damage == 0
    assert sortie.bot_damage == 0
    assert sortie.sortie_status == SortieStatus()
    assert sortie.bot_status == BotLifeStatus()



# def test_aircraft(mission, airfield_friendly, area_friendly, area_enemy):
#     """
#     :type mission: MissionReport
#     :type airfield_friendly: Airfield
#     :type area_friendly: Area
#     :type area_enemy: Area
#     """
#     aircraft = Object(mission=mission, data={
#         'id': 10011,
#         'object_name': 'La-5 ser.8',
#         'country_id': 101,
#         'parent_id': None,
#     })
#     bot = Object(mission=mission, data={
#         'id': 10012,
#         'object_name': 'BotPilot',
#         'country_id': 101,
#         'parent_id': 10011,
#     })
#
#     sortie = Sortie(mission=mission, data={
#         'aircraft_id': 10011,
#         'bot_id': 10012,
#         'pos': {'x': 7500.0, 'y': 0.0, 'z': 7500.0},
#         'account_id': '76638c27-16d7-4ee2-95be-d326a9c499b7',
#         'profile_id': '8d8a0ac5-095d-41ea-93b5-09599a5fde4c',
#         'name': 'John Doe',
#         'aircraft_name': 'La-5 ser.8',
#         'country_id': 101,
#         'airfield_id': None,
#         'airstart': False,
#         'parent_id': None,
#         'payload_id': 1,
#         'fuel': 50,
#         'skin': '',
#         'weapon_mods_id': [],
#         'tik': 20,
#         'cartridges': 500,
#         'shells': 0,
#         'bombs': 0,
#         'rockets': 0,
#     })
#
#     assert mission.objects_id_map[10011] == aircraft
#     assert mission.objects_id_map[10012] == bot
#
#     assert aircraft.id == 10011
#     assert aircraft.coal_id == 1
#     assert aircraft.country_id == 101
#     assert aircraft.parent is None
#     assert aircraft.log_name == 'la-5 ser.8'
#     assert aircraft.sortie is None
#     assert aircraft.sortie_status.is_not_takeoff
#     assert aircraft.life_status.is_unharmed
#
#     assert bot.parent == aircraft
#     assert aircraft.children[10012] == bot
#
#     aircraft.captured()
#     assert aircraft.is_captured
#     assert bot.is_captured
#
#     aircraft.update_position(data={'pos': {'x': 7500.0, 'y': 0.0, 'z': 7500.0}})
#     assert aircraft.last_pos == {'x': 7500.0, 'y': 0.0, 'z': 7500.0}
#
#     assert aircraft.is_aircraft_rtb(pos=aircraft.last_pos)
#     assert aircraft.is_on_enemy_territory(pos={'x': 25000.0, 'y': 0.0, 'z': 25000.0})
#
#     # aircraft.takeoff(data={'tik': 1})
#     # assert not aircraft.is_not_takeoff
#     # assert not aircraft.on_ground
#     # assert not aircraft.is_captured
#     # assert aircraft.sortie_status.is_in_flight
#     # assert not bot.is_captured
#     #
#     # aircraft.landing(data={'pos': {'x': 7500.0, 'y': 0.0, 'z': 7500.0}, 'tik': 1000})
#     # assert aircraft.on_ground
#     # assert not aircraft.is_captured
#     # assert aircraft.sortie_status.is_landed
#
#     # aircraft.got_damaged(damage=10)
#     # assert aircraft.life_status.is_damaged
#     # assert aircraft.damage == 10
#     # aircraft.got_damaged(damage=10)
#     # assert aircraft.damage == 20
#     #
#     # aircraft.got_killed()
#     # assert aircraft.life_status.is_destroyed
#
#     # aircraft.deinitialization()
#     # assert aircraft.is_deinitialized
#
#     # TODO доделать тесты остальных методов
