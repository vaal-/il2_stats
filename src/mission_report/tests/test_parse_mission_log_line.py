from datetime import datetime

import pytest

from ..parse_mission_log_line import parse, UnexpectedATypeWarning


def test_atype_0():
    line = ('T:0 AType:0 GDate:1942.9.19 GTime:14:0:0 MFile:Multiplayer/Dogfight\_gen.msnbin MID: GType:2 '
            'CNTRS:0:0,101:1,201:2 SETTS:000000000010000100000000110 MODS:0 PRESET:0 AQMID:0 ROUNDS: 1 POINTS: 15000')
    result = {'tik': 0, 'atype_id': 0, 'date': datetime(1942, 9, 19, 14),
              'file_path': 'Multiplayer/Dogfight\_gen.msnbin', 'game_type_id': 2,
              'countries': {0: 0, 201: 2,  101: 1},
              'settings': (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0),
              'mods': False, 'preset_id': 0}
    assert parse(line) == result


def test_atype_1():
    line = 'T:63164 AType:1 AMMO:BULLET_GER_792x57_SS AID:138247 TID:59392'
    result = {'tik': 63164, 'atype_id': 1, 'ammo': 'BULLET_GER_792x57_SS', 'attacker_id': 138247,  'target_id': 59392}
    assert parse(line) == result


def test_atype_2():
    line = 'T:524734 AType:2 DMG:0.007 AID:172089 TID:133194 POS(23876.303,119.281,28392.604)'
    result = {'tik': 524734, 'atype_id': 2, 'damage': 0.7, 'attacker_id': 172089, 'target_id': 133194,
              'pos': dict(x=23876.303, y=119.281, z=28392.604)}
    assert parse(line) == result


def test_atype_2_dmg_bug():
    line = 'T:139627 AType:2 DMG:-0.000 AID:322581 TID:287744 POS(129686.703,48.173,181686.391)'
    result = {'tik': 139627, 'atype_id': 2, 'damage': -0.0, 'attacker_id': 322581, 'target_id': 287744,
              'pos': dict(x=129686.703, y=48.173, z=181686.391)}
    assert parse(line) == result


def test_atype_2_no_actor():
    line = 'T:524734 AType:2 DMG:0.007 AID:-1 TID:133194 POS(23876.303,119.281,28392.604)'
    result = {'tik': 524734, 'atype_id': 2, 'damage': 0.7, 'attacker_id': None, 'target_id': 133194,
              'pos': dict(x=23876.303, y=119.281, z=28392.604)}
    assert parse(line) == result


def test_atype_2_pos_bug():
    line = 'T:524734 AType:2 DMG:0.007 AID:172089 TID:133194 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 524734, 'atype_id': 2, 'damage': 0.7, 'attacker_id': 172089, 'target_id': 133194, 'pos': None}
    assert parse(line) == result


def test_atype_3():
    line = 'T:26383 AType:3 AID:107527 TID:106497 POS(25131.697,744.438,23284.689)'
    result = {'tik': 26383, 'atype_id': 3, 'attacker_id': 107527,  'target_id': 106497,
              'pos': dict(x=25131.697, y=744.438, z=23284.689)}
    assert parse(line) == result


def test_atype_3_no_actor():
    line = 'T:26383 AType:3 AID:-1 TID:106497 POS(25131.697,744.438,23284.689)'
    result = {'tik': 26383, 'atype_id': 3, 'attacker_id': None,  'target_id': 106497,
              'pos': dict(x=25131.697, y=744.438, z=23284.689)}
    assert parse(line) == result


def test_atype_3_pos_bug():
    line = 'T:26383 AType:3 AID:107527 TID:106497 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 26383, 'atype_id': 3, 'attacker_id': 107527,  'target_id': 106497, 'pos': None}
    assert parse(line) == result


def test_atype_4():
    line = 'T:27071 AType:4 PLID:106497 PID:107521 BUL:869 SH:0 BOMB:0 RCT:0 (25727.014,57.894,23335.092)'
    result = {'tik': 27071, 'atype_id': 4, 'aircraft_id': 106497, 'bot_id': 107521, 'cartridges': 869, 'shells': 0,
              'bombs': 0, 'rockets': 0, 'pos': dict(x=25727.014, y=57.894, z=23335.092)}
    assert parse(line) == result


def test_atype_4_pos_bug():
    line = 'T:27071 AType:4 PLID:106497 PID:107521 BUL:869 SH:0 BOMB:0 RCT:0 (-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 27071, 'atype_id': 4, 'aircraft_id': 106497, 'bot_id': 107521, 'cartridges': 869, 'shells': 0,
              'bombs': 0, 'rockets': 0, 'pos': None}
    assert parse(line) == result


def test_atype_5():
    line = 'T:16960 AType:5 PID:109572 POS(23800.740, 116.003, 28128.986)'
    result = {'tik': 16960, 'atype_id': 5, 'aircraft_id': 109572, 'pos': dict(x=23800.74, y=116.003, z=28128.986)}
    assert parse(line) == result


def test_atype_5_pos_bug():
    line = 'T:16960 AType:5 PID:109572 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 16960, 'atype_id': 5, 'aircraft_id': 109572, 'pos': None}
    assert parse(line) == result


def test_atype_6():
    line = 'T:16960 AType:6 PID:109572 POS(23800.740, 116.003, 28128.986)'
    result = {'tik': 16960, 'atype_id': 6, 'aircraft_id': 109572, 'pos': dict(x=23800.74, y=116.003, z=28128.986)}
    assert parse(line) == result


def test_atype_6_pos_bug():
    line = 'T:16960 AType:6 PID:109572 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 16960, 'atype_id': 6, 'aircraft_id': 109572, 'pos': None}
    assert parse(line) == result


def test_atype_7():
    line = 'T:525287 AType:7 '
    result = {'tik': 525287, 'atype_id': 7}
    assert parse(line) == result


def test_atype_8():
    line = 'T:3745 AType:8 OBJID:102 POS(37286.734,0.000,18839.822) COAL:1 TYPE:0 RES:1 ICTYPE:0'
    result = {'tik': 3745, 'atype_id': 8, 'object_id': 102, 'pos': dict(x=37286.734, y=0.0, z=18839.822), 'coal_id': 1,
              'task_type_id': 0, 'success': True, 'icon_type_id': 0}
    assert parse(line) == result


def test_atype_8_pos_bug():
    line = 'T:3745 AType:8 OBJID:102 POS(-1.#QO,-1.#QO,-1.#QO) COAL:1 TYPE:0 RES:1 ICTYPE:0'
    result = {'tik': 3745, 'atype_id': 8, 'object_id': 102, 'pos': None, 'coal_id': 1,
              'task_type_id': 0, 'success': True, 'icon_type_id': 0}
    assert parse(line) == result


def test_atype_9():
    line = 'T:10 AType:9 AID:13312 COUNTRY:501 POS(30178.900, 66.126, 25254.000) IDS()'
    result = {'tik': 10, 'atype_id': 9, 'airfield_id': 13312, 'country_id': 501,
              'pos': dict(x=30178.9, y=66.126, z=25254.0), 'aircraft_id_list': []}
    assert parse(line) == result


def test_atype_9_with_ids():
    line = 'T:10 AType:9 AID:13312 COUNTRY:501 POS(30178.900, 66.126, 25254.000) IDS(0,0,0)'
    result = {'tik': 10, 'atype_id': 9, 'airfield_id': 13312, 'country_id': 501,
              'pos': dict(x=30178.9, y=66.126, z=25254.0), 'aircraft_id_list': [0, 0, 0]}
    assert parse(line) == result


def test_atype_9_pos_bug():
    line = 'T:10 AType:9 AID:13312 COUNTRY:501 POS(-1.#QO,-1.#QO,-1.#QO) IDS()'
    result = {'tik': 10, 'atype_id': 9, 'airfield_id': 13312, 'country_id': 501, 'pos': None, 'aircraft_id_list': []}
    assert parse(line) == result


def test_atype_10():
    line = ('T:504435 AType:10 PLID:32779 PID:93195 BUL:1082 SH:0 BOMB:0 RCT:0 '
            '(23732.977,36.585,26604.607) IDS:e6cfcefe-a3a1-4d0d-90e7-fe24caf27d2e '
            'LOGIN:5c6480cb-6d80-40cb-85de-e55167895b7f NAME:IRFC_Artun_Beta TYPE:Bristol F2B (F.II) COUNTRY:103 '
            'FORM:0 FIELD:235520 INAIR:0 PARENT:-1 PAYLOAD:10 FUEL:1.000 SKIN:bristolf2bf2/f2bf2_irfc_def.dds WM:3')
    result = {'tik': 504435, 'atype_id': 10, 'aircraft_id': 32779, 'bot_id': 93195, 'cartridges': 1082, 'shells': 0,
              'bombs': 0, 'rockets': 0, 'pos': dict(x=23732.977, y=36.585, z=26604.607),
              'profile_id': 'e6cfcefe-a3a1-4d0d-90e7-fe24caf27d2e', 'account_id': '5c6480cb-6d80-40cb-85de-e55167895b7f',
              'name': 'IRFC_Artun_Beta', 'aircraft_name': 'Bristol F2B (F.II)', 'country_id': 103, 'form': '0',
              'airfield_id': 235520, 'airstart': True, 'parent_id': None, 'payload_id': 10, 'fuel': 100.0,
              'skin': 'bristolf2bf2/f2bf2_irfc_def.dds', 'weapon_mods_id': [1]}
    assert parse(line) == result


def test_atype_10_pos_fuel_bug():
    line = ('T:109651 AType:10 PLID:1056791 PID:987159 BUL:340 SH:0 BOMB:0 RCT:0 (1.#QO,1.#QO,1.#QO) '
            'IDS:8d8a0ac5-095d-41ea-93b5-09599a5fde4c LOGIN:76638c27-16d7-4ee2-95be-d326a9c499b7 '
            'NAME:174driver TYPE:La-5 ser.8 COUNTRY:101 FORM:0 FIELD:0 INAIR:2 '
            'PARENT:-1 PAYLOAD:0 FUEL:-1.#QO SKIN:la5s8/la5s8_skin_01.dds WM:1')
    result = {'tik': 109651, 'atype_id': 10, 'aircraft_id': 1056791, 'bot_id': 987159, 'cartridges': 340, 'shells': 0,
              'bombs': 0, 'rockets': 0, 'pos': None, 'profile_id': '8d8a0ac5-095d-41ea-93b5-09599a5fde4c',
              'account_id': '76638c27-16d7-4ee2-95be-d326a9c499b7', 'name': '174driver',
              'aircraft_name': 'La-5 ser.8', 'country_id': 101, 'form': '0',
              'airfield_id': None, 'airstart': False, 'parent_id': None, 'payload_id': 0, 'fuel': None,
              'skin': 'la5s8/la5s8_skin_01.dds', 'weapon_mods_id': []}
    assert parse(line) == result


def test_atype_10_skin_non_breaking_unicode_space():
    line = ('T:51768 AType:10 PLID:743436 PID:840716 BUL:1200 SH:0 BOMB:0 RCT:0 (78930.883,177.770,122328.320) '
            'IDS:b2e40548-27f8-49fa-9a24-ed6bfef31a9e LOGIN:c8d4d124-2a93-43df-87ca-338f8df20614 NAME:6./ZG26_Custard '
            'TYPE:Bf 109 F-2 COUNTRY:201 FORM:0 FIELD:16384 INAIR:2 PARENT:-1 PAYLOAD:0 '
            'FUEL:1.000 SKIN:bf109f2/4k bf-109f-2 custard .dds WM:49')
    result = {'tik': 51768, 'atype_id': 10, 'aircraft_id': 743436, 'bot_id': 840716, 'cartridges': 1200, 'shells': 0,
              'bombs': 0, 'rockets': 0, 'pos': dict(x=78930.883, y=177.770, z=122328.32),
              'profile_id': 'b2e40548-27f8-49fa-9a24-ed6bfef31a9e', 'account_id': 'c8d4d124-2a93-43df-87ca-338f8df20614',
              'name': '6./ZG26_Custard', 'aircraft_name': 'Bf 109 F-2', 'country_id': 201, 'form': '0',
              'airfield_id': 16384, 'airstart': False, 'parent_id': None, 'payload_id': 0, 'fuel': 100.0,
              'skin': 'bf109f2/4k bf-109f-2 custard .dds', 'weapon_mods_id': [4, 5]}
    assert parse(line) == result


def test_atype_11():
    line = 'T:1 AType:11 GID:115711 IDS:17407,26623,35839 LID:17407'
    result = {'tik': 1, 'atype_id': 11, 'group_id': 115711, 'members_id': [17407, 26623, 35839], 'leader_id': 17407}
    assert parse(line) == result


def test_atype_12():
    line = 'T:504220 AType:12 ID:410733 TYPE:Sopwith Camel COUNTRY:102 NAME:noname PID:-1'
    result = {'tik': 504220, 'atype_id': 12, 'object_id': 410733, 'object_name': 'Sopwith Camel',
              'country_id': 102, 'name': 'noname', 'parent_id': None}
    assert parse(line) == result


def test_atype_12_parachute():
    line = 'T:171760 AType:12 ID:1266700 TYPE:CParachute_1266700 COUNTRY:101 NAME:CParachute_1266700 PID:-1'
    result = {'tik': 171760, 'atype_id': 12, 'object_id': 1266700, 'object_name': 'CParachute',
              'country_id': 101, 'name': 'CParachute_1266700', 'parent_id': None}
    assert parse(line) == result


def test_atype_12_block():
    line = 'T:53 AType:12 ID:61440 TYPE:bridge_big_1[265,1] COUNTRY:201 NAME:Bridge PID:-1'
    result = {'tik': 53, 'atype_id': 12, 'object_id': 61440, 'object_name': 'bridge_big_1', 'country_id': 201,
              'name': 'Bridge', 'parent_id': None}
    assert parse(line) == result


def test_atype_12_block_2():
    line = 'T:53 AType:12 ID:61440 TYPE:bridge_big_1[-1,-1] COUNTRY:201 NAME:Bridge PID:-1'
    result = {'tik': 53, 'atype_id': 12, 'object_id': 61440, 'object_name': 'bridge_big_1', 'country_id': 201,
              'name': 'Bridge', 'parent_id': None}
    assert parse(line) == result


def test_atype_13():
    line = 'T:0 AType:13 AID:39936 COUNTRY:501 ENABLED:1 BC(0,0,0,0,0,0,0,0)'
    result = {'tik': 0, 'atype_id': 13, 'area_id': 39936, 'country_id': 501, 'enabled': True,
              'in_air': [0, 0, 0, 0, 0, 0, 0, 0]}
    assert parse(line) == result


def test_atype_14():
    line = ('T:1 AType:14 AID:39936 BP((26968.0,74.3,22949.0),(30848.0,74.3,23891.0),(35717.0,74.3,23876.0),'
            '(55007.0,74.3,15026.0),(55001.0,74.3,55020.0),(-5018.0,74.3,55042.0),(-4991.0,74.3,34620.0),'
            '(2552.0,74.3,34401.0),(8185.0,74.3,29341.0),(17968.0,74.3,26690.0),(21055.0,74.3,27434.0),'
            '(22561.0,74.3,24669.0),(25287.6,74.3,24965.3))')
    result = {'tik': 1, 'atype_id': 14, 'area_id': 39936, 'boundary': (
        (26968.0, 74.3, 22949.0), (30848.0, 74.3, 23891.0), (35717.0, 74.3, 23876.0), (55007.0, 74.3, 15026.0),
        (55001.0, 74.3, 55020.0), (-5018.0, 74.3, 55042.0), (-4991.0, 74.3, 34620.0), (2552.0, 74.3, 34401.0),
        (8185.0, 74.3, 29341.0), (17968.0, 74.3, 26690.0), (21055.0, 74.3, 27434.0), (22561.0, 74.3, 24669.0),
        (25287.6, 74.3, 24965.3))}
    assert parse(line) == result


def test_atype_15():
    line = 'T:0 AType:15 VER:17'
    result = {'tik': 0, 'atype_id': 15, 'version': '17'}
    assert parse(line) == result


def test_atype_16_with_ids():
    line = 'T:32497 AType:16 BOTID:108551 POS(23899.598,154.684,20580.168)'
    result = {'tik': 32497, 'atype_id': 16, 'bot_id': 108551, 'pos': dict(x=23899.598, y=154.684, z=20580.168)}
    assert parse(line) == result


def test_atype_16_pos_bug():
    line = 'T:32497 AType:16 BOTID:108551 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 32497, 'atype_id': 16, 'bot_id': 108551, 'pos': None}
    assert parse(line) == result


def test_atype_17_with_ids():
    line = 'T:58 AType:17 ID:107519 POS(39013.016,45.535,16807.107)'
    result = {'tik': 58, 'atype_id': 17, 'object_id': 107519, 'pos': dict(x=39013.016, y=45.535, z=16807.107)}
    assert parse(line) == result


def test_atype_17_pos_bug():
    line = 'T:58 AType:17 ID:107519 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 58, 'atype_id': 17, 'object_id': 107519, 'pos': None}
    assert parse(line) == result


def test_atype_18():
    line = 'T:68207 AType:18 BOTID:1662987 PARENTID:1661963 POS(103313.617,358.759,168764.578)'
    result = {'tik': 68207, 'atype_id': 18, 'bot_id': 1662987, 'parent_id': 1661963,
              'pos': dict(x=103313.617, y=358.759, z=168764.578)}
    assert parse(line) == result


def test_atype_18_pos_bug():
    line = 'T:68207 AType:18 BOTID:1662987 PARENTID:1661963 POS(-1.#QO,-1.#QO,-1.#QO)'
    result = {'tik': 68207, 'atype_id': 18, 'bot_id': 1662987, 'parent_id': 1661963, 'pos': None}
    assert parse(line) == result


def test_atype_19():
    line = 'T:706771 AType:19 '
    result = {'tik': 706771, 'atype_id': 19}
    assert parse(line) == result


def test_atype_20():
    line = 'T:2126 AType:20 USERID:3cf05e60-809a-4c12-bfa4-832f6d282f0d USERNICKID:19ce5f28-1bd6-4116-9e5e-fbe1cb955da3'
    result = {'tik': 2126, 'atype_id': 20, 'account_id': '3cf05e60-809a-4c12-bfa4-832f6d282f0d',
              'profile_id': '19ce5f28-1bd6-4116-9e5e-fbe1cb955da3'}
    assert parse(line) == result


def test_atype_21():
    line = 'T:2126 AType:21 USERID:3cf05e60-809a-4c12-bfa4-832f6d282f0d USERNICKID:19ce5f28-1bd6-4116-9e5e-fbe1cb955da3'
    result = {'tik': 2126, 'atype_id': 21, 'account_id': '3cf05e60-809a-4c12-bfa4-832f6d282f0d',
              'profile_id': '19ce5f28-1bd6-4116-9e5e-fbe1cb955da3'}
    assert parse(line) == result


def test_atype_unknown():
    line = 'T:58 AType:25 VER:17'
    with pytest.raises(UnexpectedATypeWarning):
        parse(line)
