"""
examples:

# Tour awards
# available parameters stats/models.py/class Player


# streak 100 or more
def fighter_ace(player):
    return player.streak_max >= 100


# total air kills 20 or more
def example_2(player):
    if player.ak_total >= 20:
        return True


# 20 air kills and 200 ground kills
def example_3(player):
    return player.ak_total >= 20 and player.gk_total >= 200


# Sortie awards
# available parameters stats/models.py/class Sortie


# 5 air kills in one sortie
def fighter_hero(sortie):
    return sortie.ak_total >= 5


# Mission awards
# available parameters stats/models.py/class PlayerMission


# 10 air kills in one mission
def mission_fighter_hero(player_mission):
    return player_mission.ak_total >= 15

"""


# streak 100 or more
def fighter_ace(player):
    return player.streak_max >= 100


# 5 air kills in one sortie
def fighter_hero(sortie):
    return sortie.ak_total >= 5


# 15 air kills in one mission
def mission_hero(player_mission):
    return player_mission.ak_total >= 15


# 15 air kills in one virtual life
def vlife_hero(vlife):
    return vlife.ak_total >= 25
