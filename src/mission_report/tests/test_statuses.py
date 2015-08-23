from ..statuses import SortieStatus, LifeStatus, BotLifeStatus


def test_sortie_status():
    sortie_status = SortieStatus()
    assert sortie_status.is_not_takeoff

    sortie_status = SortieStatus(is_airstart=True)
    assert sortie_status.is_in_flight

    sortie_status.landing()
    assert sortie_status.is_landed
    assert sortie_status.on_ground

    sortie_status.ditch()
    assert sortie_status.is_ditched
    assert sortie_status.on_ground

    sortie_status.crash()
    assert sortie_status.is_crashed
    assert sortie_status.on_ground

    sortie_status.down()
    assert sortie_status.is_shotdown


def test_life_status():
    life_status = LifeStatus()
    assert life_status.is_unharmed

    life_status.damage()
    assert life_status.is_damaged

    life_status.destroy()
    assert life_status.is_destroyed

    life_status.damage()
    assert not life_status.is_damaged


def test_bot_life_status():
    bot_life_status = BotLifeStatus()
    assert bot_life_status.is_healthy

    bot_life_status.damage()
    assert bot_life_status.is_wounded

    bot_life_status.destroy()
    assert bot_life_status.is_dead

    bot_life_status.damage()
    assert not bot_life_status.is_wounded
