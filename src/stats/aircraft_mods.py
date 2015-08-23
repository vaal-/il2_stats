import functools

from django.utils.translation import pgettext_lazy


@functools.lru_cache(maxsize=1024)
def get_aircraft_mods(aircraft, id_list):
    mods = []
    for id in id_list:
        try:
            mod = aircraft_mods[aircraft][id]
            mods.append(mod)
        except KeyError:
            pass
    return mods


aircraft_mods = {
    'bf 109 e-7': {
        3: pgettext_lazy('aircraft_mod', 'Armoured Wind Screen'),
        4: pgettext_lazy('aircraft_mod', 'Removed Headrest'),
        5: pgettext_lazy('aircraft_mod', 'Additional armour plates'),
    },
    'bf 109 f-2': {
        4: pgettext_lazy('aircraft_mod', 'Armoured Wind Screen'),
        5: pgettext_lazy('aircraft_mod', 'Removed Headrest'),
    },
    'bf 109 f-4': {
        4: pgettext_lazy('aircraft_mod', 'Armoured Wind Screen'),
        5: pgettext_lazy('aircraft_mod', 'Removed Headrest'),
    },
    'bf 109 g-2': {
        4: pgettext_lazy('aircraft_mod', 'Armoured Glass Head Rest'),
        5: pgettext_lazy('aircraft_mod', 'Removed Headrest'),
    },
    'bf 110 e-2': {
        1: pgettext_lazy('aircraft_mod', 'Armoured Wind Screen'),
        2: pgettext_lazy('aircraft_mod', 'Additional armour plates'),
    },
    'he 111 h-6': {
        1: pgettext_lazy('aircraft_mod', 'Belly 20mm gun turret'),
        2: pgettext_lazy('aircraft_mod', 'Nose 20mm gun turret'),
    },
    'i-16 type 24': {
        4: pgettext_lazy('aircraft_mod', 'One-piece Windscreen'),
    },
    'il-2 mod.1942': {
        5: pgettext_lazy('aircraft_mod', 'Rear turret'),
    },
    'ju 87 d-3': {
        1: pgettext_lazy('aircraft_mod', 'Siren'),
        3: pgettext_lazy('aircraft_mod', 'Additional armour plates'),
    },
    'la-5 ser.8': {
        3: pgettext_lazy('aircraft_mod', 'RPK-10'),
        4: pgettext_lazy('aircraft_mod', 'Flat Windscreen'),
    },
    'mc.202 ser.viii': {
        1: pgettext_lazy('aircraft_mod', 'Armoured Wind Screen'),
    },
    'pe-2 ser.35': {
        5: pgettext_lazy('aircraft_mod', 'RPK-2'),
    },
    'pe-2 ser.87': {
        5: pgettext_lazy('aircraft_mod', 'Blister turret'),
    },
    'yak-1 ser.69': {
        5: pgettext_lazy('aircraft_mod', 'RPK-10'),
    },
}
