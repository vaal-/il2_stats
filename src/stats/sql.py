from django.conf import settings
from django.db import connection
from django.utils import timezone


INACTIVE_PLAYER_DAYS = settings.INACTIVE_PLAYER_DAYS
SQUAD_MEMBERS_MINIMUM = settings.SQUAD_MEMBERS_MINIMUM


def get_squad_position_by_field(squad, field):
    field_value = getattr(squad, field)
    params = {'field': field, 'field_value': field_value, 'profile_id': squad.profile_id,
              'tour_id': squad.tour_id, 'num_members': SQUAD_MEMBERS_MINIMUM}
    with connection.cursor() as cursor:
        sql = '''
            SELECT position
            FROM (
                SELECT
                     ROW_NUMBER() OVER (ORDER BY squads_stats.{field} DESC, squads_stats.id) AS position,
                     squads_stats.profile_id as profile_id
                FROM squads_stats, squads
                WHERE
                    squads_stats.num_members >= {num_members} AND
                    squads_stats.profile_id = squads.id AND
                    squads_stats.tour_id = {tour_id} AND
                    squads_stats.{field} >= {field_value}
            ) sub
            WHERE
                profile_id = {profile_id}
        '''

        cursor.execute(sql.format(**params))
        try:
            return cursor.fetchone()[0]
        except (IndexError, TypeError):
            return 0


# http://stackoverflow.com/questions/907438/can-i-get-the-position-of-a-record-in-a-sql-result-table
def get_position_by_field(player, field):
    field_value = getattr(player, field)
    params = {'field': field, 'field_value': field_value, 'profile_id': player.profile_id,
              'type': player.type, 'tour_id': player.tour_id}
    with connection.cursor() as cursor:
        if INACTIVE_PLAYER_DAYS:
            if player.tour.is_ended:
                params['date'] = player.tour.date_end - INACTIVE_PLAYER_DAYS
            else:
                params['date'] = timezone.now() - INACTIVE_PLAYER_DAYS
            sql = '''
                SELECT position
                FROM (
                    SELECT
                        ROW_NUMBER() OVER (ORDER BY players.{field} DESC, players.id) AS position,
                        players.profile_id as profile_id
                    FROM players, profiles
                    WHERE
                        players.profile_id = profiles.id AND
                        players.type = '{type}' AND
                        players.tour_id = {tour_id} AND
                        players.date_last_combat > '{date}' AND
                        players.{field} >= {field_value} AND
                        profiles.is_hide = FALSE
                ) sub
                WHERE
                    profile_id = {profile_id}

            '''
        else:
            sql = '''
                SELECT position
                FROM (
                    SELECT
                         ROW_NUMBER() OVER (ORDER BY players.{field} DESC, players.id) AS position,
                         players.profile_id as profile_id
                    FROM players, profiles
                    WHERE
                        players.profile_id = profiles.id AND
                        players.type = '{type}' AND
                        players.tour_id = {tour_id} AND
                        players.{field} >= {field_value} AND
                        profiles.is_hide = FALSE
                ) sub
                WHERE
                    profile_id = {profile_id}
            '''

        cursor.execute(sql.format(**params))
        try:
            return cursor.fetchone()[0]
        except (IndexError, TypeError):
            return 0


def get_nicknames(profile_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT nickname FROM sorties WHERE profile_id = %s GROUP BY nickname', (profile_id,))
        return [name[0] for name in cursor.fetchall()]
