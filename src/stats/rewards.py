from functools import lru_cache

from custom import rewards
from stats.models import Award, Reward


_awards_tour = Award.objects.filter(type='tour')
_awards_mission = Award.objects.filter(type='mission')
_awards_sortie = Award.objects.filter(type='sortie')


@lru_cache(maxsize=32)
def get_reward_func(func_name):
    return getattr(rewards, func_name)


@lru_cache(maxsize=512)
def rewarding(award_id, player_id):
    return Reward.objects.get_or_create(award_id=award_id, player_id=player_id)


def reward_tour(player):
    for award in _awards_tour:
        if get_reward_func(award.func)(player=player):
            rewarding(award_id=award.id, player_id=player.id)


def reward_mission(player_mission):
    player = player_mission.player
    for award in _awards_mission:
        if get_reward_func(award.func)(player_mission=player_mission):
            rewarding(award_id=award.id, player_id=player.id)


def reward_sortie(sortie):
    player = sortie.player
    for award in _awards_sortie:
        if get_reward_func(award.func)(sortie=sortie):
            rewarding(award_id=award.id, player_id=player.id)
