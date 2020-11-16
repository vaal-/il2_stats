from copy import deepcopy
import logging

from mission_report import parse_mission_log_line
from mission_report.constants import COUNTRIES_COALITION_DEFAULT, COALITION_ALIAS
from stats.models import PlayerOnline, Profile


logger = logging.getLogger('online')


_countries = deepcopy(COUNTRIES_COALITION_DEFAULT)


def update_online(m_report_files, online_timestamp):
    for file_path in m_report_files:
        if file_path.stat().st_mtime > online_timestamp:
            online_timestamp = file_path.stat().st_mtime
            with file_path.open() as f:
                for line in f:
                    # игнорируем "плохие" строки без
                    if 'AType' not in line:
                        logger.warning('ignored bad string: [{}]'.format(line))
                        continue
                    try:
                        data = parse_mission_log_line.parse(line)
                    except parse_mission_log_line.UnexpectedATypeWarning:
                        logger.warning('unexpected atype: [{}]'.format(line))
                        continue

                    atype_id = data.pop('atype_id')

                    if atype_id == 10:
                        try:
                            profile = Profile.objects.get(uuid=data['account_id'])
                        except Profile.DoesNotExist:
                            profile = None
                        PlayerOnline.objects.update_or_create(uuid=data['account_id'], defaults={
                            'nickname': data['name'],
                            'coalition': _countries[data['country_id']],
                            'profile': profile,
                        })
                    elif atype_id == 21:
                        PlayerOnline.objects.filter(uuid=data['account_id']).delete()
                    elif atype_id == 0:
                        for country, coalition in data['countries'].items():
                            _countries[country] = COALITION_ALIAS[coalition]

    return online_timestamp


def cleanup_online():
    PlayerOnline.objects.all().delete()
