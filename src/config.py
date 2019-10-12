import configparser
from pathlib import Path
import os

from tzlocal import get_localzone

from core.settings import DATABASES

DEFAULT = {
    'http': {
        'host': '127.0.0.1',
        'port': 8000,
    },
    'database': {
        'host': '127.0.0.1',
        'port': 5432,
        'name': 'database-name',
        'user': 'username',
        'password': 'password',
    },
    'game_server': {
        'path': r'C:\Program Files (x86)\1C Game Studios\IL-2 Sturmovik Battle of Stalingrad',
        # 'time_zone': 'Europe/Moscow',
        'time_zone': get_localzone().zone,
    },
    'stats': {
        'mission_report_path': '',
        'mission_report_delete': True,
        'mission_report_backup_days': 31,
        'inactive_player_days': 7,
        'new_tour_by_month': True,
        'win_by_score': True,
        'win_score_min': 2000,
        'win_score_ratio': 1.5,
        'sortie_min_time': 0,
        'skin_id': 1,
    },
    'email': {
        'send_email': False,
        'from_email': '',
        'email_host': '',
        'email_host_password': '',
        'email_host_user': '',
        'email_port': 25,
        'email_use_tls': False,
        'email_use_ssl': False,
    }
}


def get_conf():
    conf = configparser.ConfigParser(empty_lines_in_values=False)
    conf.read_dict(DEFAULT)
    with open('conf.ini', encoding='utf-8-sig') as f:
        conf.read_file(f)
    # conf = conf._sections
    game_path = Path(conf['game_server']['path'])
    startup_path = game_path.joinpath('data', 'startup.cfg')
    with startup_path.open() as f:
        startup_string = '\n'.join([line.strip() for line in f if '[END]' not in line])
        startup_cfg = configparser.ConfigParser()
        startup_cfg.read_string(startup_string)
        text_log_folder = startup_cfg['KEY = system'].get('text_log_folder', '').replace('"', '')
        conf['stats']['mission_report_path'] = text_log_folder
    return conf

conf = get_conf()

HTTP_HOST = conf['http']['host']
HTTP_PORT = int(conf['http']['port'])

DATABASES['default']['HOST'] = conf['database']['host']
DATABASES['default']['PORT'] = conf['database'].getint('port')
DATABASES['default']['NAME'] = conf['database']['name']
DATABASES['default']['USER'] = conf['database']['user']
DATABASES['default']['PASSWORD'] = conf['database']['password']

GAME_SERVER_PATH = conf['game_server']['path']

if os.name == 'nt':
    # windows
    conf['stats']['mission_report_path'] = conf['stats']['mission_report_path'].replace('/', '\\')
else:
    # nix
    conf['stats']['mission_report_path'] = conf['stats']['mission_report_path'].replace('\\', '/')

# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
MISSION_REPORT_TZ = conf['game_server']['time_zone']
MISSION_REPORT_PATH = Path(conf['game_server']['path'], 'data').joinpath(conf['stats']['mission_report_path'])
MISSION_REPORT_DELETE = conf['stats'].getboolean('mission_report_delete')
MISSION_REPORT_BACKUP_DAYS = conf['stats'].getint('mission_report_backup_days')
MISSION_REPORT_BACKUP_PATH = MISSION_REPORT_PATH.joinpath('mission_report_backup')

INACTIVE_PLAYER_DAYS = conf['stats'].getint('inactive_player_days')
NEW_TOUR_BY_MONTH = conf['stats'].getboolean('new_tour_by_month')
WIN_BY_SCORE = conf['stats'].getboolean('win_by_score')
WIN_SCORE_MIN = conf['stats'].getint('win_score_min')
WIN_SCORE_RATIO = conf['stats'].getfloat('win_score_ratio')
SORTIE_MIN_TIME = conf['stats'].getint('sortie_min_time')
SKIN_ID = conf['stats'].getint('skin_id')

SEND_EMAIL = conf['email'].getboolean('send_email')
DEFAULT_FROM_EMAIL = conf['email']['from_email']
EMAIL_HOST = conf['email']['email_host']
EMAIL_HOST_PASSWORD = conf['email']['email_host_password']
EMAIL_HOST_USER = conf['email']['email_host_user']
EMAIL_PORT = conf['email'].getint('email_port')
EMAIL_USE_TLS = conf['stats'].getboolean('email_use_tls')
EMAIL_USE_SSL = conf['email'].getboolean('email_use_ssl')
