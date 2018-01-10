from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE killboard_pvp RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE log_entries RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE missions RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE online RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE players RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE players_aircraft RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE players_missions RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE rewards RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE sorties RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE squads_stats RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE tours RESTART IDENTITY CASCADE')
        cursor.execute('TRUNCATE TABLE vlifes RESTART IDENTITY CASCADE')
        print('Statistics reseted')
