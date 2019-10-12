from datetime import timedelta

from django.conf import settings
from django.db.models import Q, Count, Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from mission_report.constants import Coalition

from .helpers import Paginator, get_sort_by, redirect_fix_url
from .models import (Player, Mission, PlayerMission, PlayerAircraft, Sortie, KillboardPvP,
                     Tour, LogEntry, Profile, Squad, Reward, PlayerOnline, VLife)
from . import sortie_log


INACTIVE_PLAYER_DAYS = settings.INACTIVE_PLAYER_DAYS
ITEMS_PER_PAGE = 20


missions_sort_fields = ['id', 'pilots_total', 'winning_coalition', 'duration']
squads_sort_fields = ['ak_total', 'gk_total', 'flight_time', 'kd', 'khr', 'score', 'rating', 'num_members']
pilots_sort_fields = ['ak_total', 'streak_current', 'gk_total', 'flight_time', 'kd', 'khr', 'accuracy', 'score', 'rating']
killboard_sort_fields = ['won', 'lose', 'wl']


def _get_rating_position(item, field='rating'):
    rating_position = item.get_position_by_field(field=field)
    if rating_position:
        page_position = rating_position // ITEMS_PER_PAGE
        if rating_position % ITEMS_PER_PAGE:
            page_position += 1
    else:
        page_position = None
    return rating_position, page_position


def _get_squad(request, squad_id):
    tour_id = request.GET.get('tour')
    # ищем сквад подходящий по туру
    if tour_id:
        try:
            return Squad.squads.get(profile_id=squad_id, tour_id=request.tour.id)
        except Squad.DoesNotExist:
            pass
    # если не нашли сквад в текущем туре - ищем сквад в другом туре, если сквада нет вообще - кидаем 404
    try:
        return Squad.squads.filter(profile_id=squad_id).order_by('-id')[0]
    except IndexError:
        raise Http404


def squad(request, squad_id, squad_tag=None):
    squad_ = _get_squad(request=request, squad_id=squad_id)
    if squad_.tag != squad_tag:
        return redirect_fix_url(request=request, param='squad_tag', value=squad_.tag)
    # подменяем тур на случай если выдаем другой
    request.tour = squad_.tour
    rating_position, page_position = _get_rating_position(item=squad_)
    return render(request, 'squad.html', {
        'squad': squad_,
        'rating_position': rating_position,
        'page_position': page_position,
    })


def squad_pilots(request, squad_id, squad_tag=None):
    squad_ = _get_squad(request=request, squad_id=squad_id)
    if squad_.tag != squad_tag:
        return redirect_fix_url(request=request, param='squad_tag', value=squad_.tag)
    # подменяем тур на случай если выдаем другой
    request.tour = squad_.tour
    sort_by = get_sort_by(request=request, sort_fields=pilots_sort_fields, default='-rating')
    pilots = Player.players.pilots(tour_id=squad_.tour_id, squad_id=squad_.id).order_by(sort_by, 'id')
    return render(request, 'squad_pilots.html', {'squad': squad_, 'pilots': pilots})


def squad_rankings(request):
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()
    sort_by = get_sort_by(request=request, sort_fields=squads_sort_fields, default='-rating')
    squads = Squad.squads.filter(tour_id=request.tour.id).order_by(sort_by, 'id')
    if search:
        squads = squads.search(name=search)
    else:
        squads = squads.active()
    squads = Paginator(squads, ITEMS_PER_PAGE).page(page)
    return render(request, 'squads.html', {
        'squads': squads,
        'sort_by': sort_by,
    })


def pilot_rankings(request):
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()
    sort_by = get_sort_by(request=request, sort_fields=pilots_sort_fields, default='-rating')
    players = Player.players.pilots(tour_id=request.tour.id).order_by(sort_by, 'id')
    if search:
        players = players.search(name=search)
    else:
        players = players.active(tour=request.tour)
    players = Paginator(players, ITEMS_PER_PAGE).page(page)
    return render(request, 'pilots.html', {
        'players': players,
        'sort_by': sort_by,
    })


def pilot(request, profile_id, nickname=None):
    tour_id = request.GET.get('tour')
    if tour_id:
        try:
            player = (Player.objects.select_related('profile', 'tour')
                      .get(profile_id=profile_id, type='pilot', tour_id=request.tour.id))
        except Player.DoesNotExist:
            try:
                profile = Profile.objects.get(id=profile_id)
                return render(request, 'pilot_not_exist.html', {'profile': profile})
            except Profile.DoesNotExist:
                raise Http404
    else:
        try:
            player = (Player.objects.select_related('profile', 'tour')
                      .filter(profile_id=profile_id, type='pilot').order_by('-id')[0])
            request.tour = player.tour
        except IndexError:
            raise Http404

    if player.nickname != nickname:
        return redirect_fix_url(request=request, param='nickname', value=player.nickname)
    if player.profile.is_hide:
        return render(request, 'pilot_hide.html', {'player': player})

    try:
        fav_aircraft = (PlayerAircraft.objects
                        .select_related('aircraft')
                        .filter(player_id=player.id, aircraft__cls_base='aircraft')
                        .order_by('-sorties_total')[0])
    except IndexError:
        fav_aircraft = None

    rating_position, page_position = _get_rating_position(item=player)

    return render(request, 'pilot.html', {
        'fav_aircraft': fav_aircraft,
        'player': player,
        'rating_position': rating_position,
        'page_position': page_position,
    })


def pilot_awards(request, profile_id, nickname=None):
    try:
        player = (Player.objects.select_related('profile', 'tour')
                  .get(profile_id=profile_id, type='pilot', tour_id=request.tour.id))
    except Player.DoesNotExist:
        raise Http404

    if player.nickname != nickname:
        return redirect_fix_url(request=request, param='nickname', value=player.nickname)
    if player.profile.is_hide:
        return render(request, 'pilot_hide.html', {'player': player})

    rewards = Reward.objects.select_related('award').filter(player_id=player.id).order_by('-date')

    return render(request, 'pilot_awards.html', {
        'player': player,
        'rewards': rewards,
    })


def pilot_killboard(request, profile_id, nickname=None):
    try:
        player = (Player.objects.select_related('profile', 'tour')
                  .get(profile_id=profile_id, type='pilot', tour_id=request.tour.id))
    except Player.DoesNotExist:
        raise Http404

    if player.nickname != nickname:
        return redirect_fix_url(request=request, param='nickname', value=player.nickname)
    if player.profile.is_hide:
        return render(request, 'pilot_hide.html', {'player': player})

    _killboard = (KillboardPvP.objects
                  .select_related('player_1__profile', 'player_2__profile')
                  .filter(Q(player_1_id=player.id) | Q(player_2_id=player.id)))
    killboard = []
    for k in _killboard:
        if k.player_1_id == player.id:
            killboard.append({'player': k.player_2, 'won': k.won_1, 'lose': k.won_2, 'wl': k.wl_1})
        else:
            killboard.append({'player': k.player_1, 'won': k.won_2, 'lose': k.won_1, 'wl': k.wl_2})

    _sort_by = get_sort_by(request=request, sort_fields=killboard_sort_fields, default='-wl')
    sort_reverse = True if _sort_by.startswith('-') else False
    sort_by = _sort_by.replace('-', '')
    killboard = sorted(killboard, key=lambda x: x[sort_by], reverse=sort_reverse)

    return render(request, 'pilot_killboard.html', {
        'player': player,
        'killboard': killboard,
    })


def pilot_sorties(request, profile_id, nickname=None):
    try:
        player = (Player.objects.select_related('profile', 'tour')
                  .get(profile_id=profile_id, type='pilot', tour_id=request.tour.id))
    except Player.DoesNotExist:
        raise Http404

    if player.nickname != nickname:
        return redirect_fix_url(request=request, param='nickname', value=player.nickname)
    if player.profile.is_hide:
        return render(request, 'pilot_hide.html', {'player': player})
    sorties = (Sortie.objects.select_related('aircraft', 'mission')
               .filter(player_id=player.id).exclude(status='not_takeoff').order_by('-id'))
    page = request.GET.get('page', 1)
    sorties = Paginator(sorties, ITEMS_PER_PAGE).page(page)
    return render(request, 'pilot_sorties.html', {
        'player': player,
        'sorties': sorties,
    })


def pilot_sortie(request, sortie_id):
    try:
        sortie = (Sortie.objects
                  .select_related('player', 'player__profile', 'player__tour', 'mission')
                  .get(id=sortie_id, player__type='pilot'))
    except Sortie.DoesNotExist:
        raise Http404
    return render(request, 'pilot_sortie.html', {
        'player': sortie.player,
        'sortie': sortie,
        'score_dict': sortie.mission.score_dict,
    })


def pilot_sortie_log(request, sortie_id):
    try:
        sortie = Sortie.objects.select_related('player', 'player__profile', 'player__tour', 'mission').get(id=sortie_id)
    except Sortie.DoesNotExist:
        raise Http404
    events = (LogEntry.objects
              .select_related('act_object', 'act_sortie', 'cact_object', 'cact_sortie')
              .filter(Q(act_sortie_id=sortie.id) | Q(cact_sortie_id=sortie.id))
              .exclude(Q(act_object__cls='trash') | Q(cact_object__cls='trash') | Q(type='shotdown', act_object__isnull=True))
              .order_by('tik'))
    for e in events:
        is_friendly_fire = e.extra_data.get('is_friendly_fire', False)
        if e.cact_sortie and e.cact_sortie.id == sortie.id:
            e.message = sortie_log.get_message(act_type='cact', event_type=e.type, has_opponent=e.act_object)
            e.color = sortie_log.get_color(act_type='cact', event_type=e.type, is_friendly_fire=is_friendly_fire)
            e.opponent_sortie = e.act_sortie
            e.opponent_object = e.act_object
            e.opponent_act = True
        elif e.act_sortie and e.act_sortie.id == sortie.id:
            e.message = sortie_log.get_message(act_type='act', event_type=e.type, has_opponent=e.cact_object)
            e.color = sortie_log.get_color(act_type='act', event_type=e.type, is_friendly_fire=is_friendly_fire)
            e.opponent_sortie = e.cact_sortie
            e.opponent_object = e.cact_object
            e.opponent_act = False

    return render(request, 'pilot_sortie_log.html', {
        'player': sortie.player,
        'sortie': sortie,
        'events': events,
    })


def missions_list(request):
    page = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()
    sort_by = get_sort_by(request=request, sort_fields=missions_sort_fields, default='-id')
    missions = Mission.objects.filter(tour_id=request.tour.id, is_hide=False).order_by(sort_by)
    if search:
        missions = missions.filter(name__icontains=search)
    missions = Paginator(missions, ITEMS_PER_PAGE).page(page)
    return render(request, 'missions.html', {
        'missions': missions,
        'sort_by': sort_by,
    })


def mission(request, mission_id):
    mission_ = get_object_or_404(Mission, id=mission_id)
    sort_by = request.GET.get('sort_by', '-score')
    if sort_by.replace('-', '') not in pilots_sort_fields:
        return redirect('stats:players_list', permanent=False)
    players = (PlayerMission.objects.select_related('player', 'profile')
               .filter(mission_id=mission_id, player__type='pilot')
               # .only('profile_id', 'player__tour_id', 'ak_total', 'gk_total', 'flight_time',
               #       'kd', 'khr', 'accuracy', 'score', 'sorties_coal', 'sorties_total')
               .order_by(sort_by, '-flight_time'))

    summary_total = mission_.stats_summary_total()
    summary_coal = mission_.stats_summary_coal()

    return render(request, 'mission.html', {
        'mission': mission_,
        'players': players,
        'sort_by': sort_by,
        'summary_total': summary_total,
        'summary_coal': summary_coal,
    })


def main(request):
    if request.tour.is_ended:
        return tour(request)
    missions_wins = request.tour.missions_wins()
    missions_wins_total = sum(missions_wins.values())

    summary_total = request.tour.stats_summary_total()
    summary_coal = request.tour.stats_summary_coal()

    top_streak = (Player.players.pilots(tour_id=request.tour.id)
                  .exclude(score_streak_current=0)
                  .active(tour=request.tour).order_by('-score_streak_current')[:10])

    top_24_score = (Sortie.objects
                    .filter(tour_id=request.tour.id, is_disco=False, player__type='pilot', profile__is_hide=False)
                    .filter(date_start__gt=timezone.now()-timedelta(hours=24))
                    .exclude(score=0)
                    .values('player')
                    .annotate(sum_score=Sum('score'))
                    .order_by('-sum_score')[:10])
    top_24_pilots = (Player.players.pilots(tour_id=request.tour.id)
                     .filter(id__in=[s['player'] for s in top_24_score]))
    top_24_pilots = {p.id: p for p in top_24_pilots}
    top_24 = []
    for p in top_24_score:
        top_24.append((top_24_pilots[p['player']], p['sum_score']))

    coal_active_players = request.tour.coal_active_players()
    total_active_players = sum(coal_active_players.values())

    try:
        previous_tour = Tour.objects.exclude(id=request.tour.id).order_by('-id')[0]
    except IndexError:
        previous_tour = None
    if previous_tour:
        previous_tour_top = (Player.players.pilots(tour_id=previous_tour.id)
                             .active(tour=previous_tour).order_by('-rating')[:20])
    else:
        previous_tour_top = None

    coal_1_online = PlayerOnline.objects.filter(coalition=Coalition.coal_1).count()
    coal_2_online = PlayerOnline.objects.filter(coalition=Coalition.coal_2).count()
    total_online = coal_1_online + coal_2_online

    return render(request, 'main.html', {
        'tour': request.tour,
        'missions_wins': missions_wins,
        'missions_wins_total': missions_wins_total,
        'summary_total': summary_total,
        'summary_coal': summary_coal,
        'top_streak': top_streak,
        'top_24': top_24,
        'coal_active_players': coal_active_players,
        'total_active_players': total_active_players,
        'previous_tour': previous_tour,
        'previous_tour_top': previous_tour_top,
        'total_online': total_online,
        'coal_1_online': coal_1_online,
        'coal_2_online': coal_2_online,
    })


def tour(request):
    missions_wins = request.tour.missions_wins()
    missions_wins_total = sum(missions_wins.values())

    summary_total = request.tour.stats_summary_total()
    summary_coal = request.tour.stats_summary_coal()

    top_streak = (Player.players.pilots(tour_id=request.tour.id)
                  .exclude(score_streak_max=0)
                  .active(tour=request.tour).order_by('-score_streak_max')[:10])

    top_rating = (Player.players.pilots(tour_id=request.tour.id)
                  .exclude(rating=0)
                  .active(tour=request.tour).order_by('-rating')[:10])

    coal_active_players = request.tour.coal_active_players()
    total_active_players = sum(coal_active_players.values())

    return render(request, 'tour.html', {
        'tour': request.tour,
        'missions_wins': missions_wins,
        'missions_wins_total': missions_wins_total,
        'summary_total': summary_total,
        'summary_coal': summary_coal,
        'top_streak': top_streak,
        'top_rating': top_rating,
        'coal_active_players': coal_active_players,
        'total_active_players': total_active_players,
    })


def online(request):
    players_coal_1 = PlayerOnline.objects.filter(coalition=Coalition.coal_1).order_by('nickname')
    players_coal_2 = PlayerOnline.objects.filter(coalition=Coalition.coal_2).order_by('nickname')

    total_coal_1 = len(players_coal_1)
    total_coal_2 = len(players_coal_2)
    total_players = total_coal_1 + total_coal_2

    return render(request, 'online.html', {
        'tour': request.tour,
        'players_coal_1': players_coal_1,
        'players_coal_2': players_coal_2,
        'total_players': total_players,
        'total_coal_1': total_coal_1,
        'total_coal_2': total_coal_2,
    })


def pilot_vlifes(request, profile_id, nickname=None):
    try:
        player = (Player.objects.select_related('profile', 'tour')
                  .get(profile_id=profile_id, type='pilot', tour_id=request.tour.id))
    except Player.DoesNotExist:
        raise Http404

    if player.nickname != nickname:
        return redirect_fix_url(request=request, param='nickname', value=player.nickname)
    if player.profile.is_hide:
        return render(request, 'pilot_hide.html', {'player': player})
    vlifes = VLife.objects.filter(player_id=player.id).exclude(sorties_total=0).order_by('-id')
    page = request.GET.get('page', 1)
    vlifes = Paginator(vlifes, ITEMS_PER_PAGE).page(page)
    return render(request, 'pilot_vlifes.html', {
        'player': player,
        'vlifes': vlifes,
    })


def pilot_vlife(request, vlife_id):
    try:
        vlife = (VLife.objects
                 .select_related('player', 'player__profile', 'player__tour')
                 .get(id=vlife_id, player__type='pilot'))
    except VLife.DoesNotExist:
        raise Http404
    return render(request, 'pilot_vlife.html', {
        'player': vlife.player,
        'vlife': vlife,
    })
