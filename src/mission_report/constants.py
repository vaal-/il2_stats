
class Coalition:
    neutral = 0
    coal_1 = 1
    coal_2 = 2

    Allies = 1
    Axis = 2
    Entente = 3
    CentralPowers = 4


class Country:
    neutral = 0
    USSR = 101
    GreatBritain = 102
    USA = 103
    Germany = 201
    Italy = 202
    Japan = 203
    France = 301
    GreatBritainWW1 = 302
    UnitedStatesWW1 = 303
    Belgium = 304
    Russia = 305
    GermanyWW1 = 401
    AustriaHungary = 402


COALITION_ALIAS = {
    0: Coalition.neutral,
    1: Coalition.coal_1,
    2: Coalition.coal_2,
    3: Coalition.coal_1,
    4: Coalition.coal_2,
}

