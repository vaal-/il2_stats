import pytest

from ..report import Airfield, Area, MissionReport, Object, Sortie


@pytest.fixture
def mission():
    mission_ = MissionReport(objects={
        'la-5 ser.8': {'cls': 'aircraft_light', 'cls_base': 'aircraft'},
        'botpilot': {'cls': 'aircraft_pilot', 'cls_base': 'crew'},
    })
    mission_.countries = {101: 1, 201: 2}
    return mission_


@pytest.fixture
def airfield_friendly(mission):
    airfield_ = Airfield(mission=mission, data={
        'id': 10001,
        'country_id': 101,
        'pos': {'x': 7500.0, 'y': 0.0, 'z': 7500.0},
    })
    return airfield_


@pytest.fixture
def area_friendly(mission):
    area_ = Area(mission=mission, data={
        'id': 10002,
        'country_id': 101,
        'enabled': True,
        'in_air': [0, 0, 0, 0, 0, 0, 0, 0],
    })
    area_.boundary = [[0, 0, 0], [15000, 0, 0], [15000, 0, 15000], [0, 0, 15000]]
    return area_


@pytest.fixture
def area_enemy(mission):
    area_ = Area(mission=mission, data={
        'id': 10003,
        'country_id': 201,
        'enabled': True,
        'in_air': [0, 0, 0, 0, 0, 0, 0, 0],
    })
    area_.boundary = [[15000, 0, 15000], [30000, 0, 15000], [30000, 0, 30000], [15000, 0, 30000]]
    return area_

