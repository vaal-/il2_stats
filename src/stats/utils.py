from django.utils.translation import ugettext_lazy as _, ungettext


def seconds_to_time(total_seconds, fmt):
    total_minutes, seconds = divmod(total_seconds, 60)
    total_hours, minutes = divmod(total_minutes, 60)
    if fmt == 'hms':
        return '%s:%02d:%02d' % (total_hours, minutes, seconds)
    elif fmt == 'HMS':
        if total_hours and minutes:
            return '%s %s %s %s' % (total_hours, ungettext('hour', 'hours', total_hours),
                                    minutes, ungettext('minute', 'minutes', minutes))
        elif total_hours:
            return '%s %s' % (total_hours, ungettext('hour', 'hours', total_hours))
        elif minutes and seconds:
            return '%s %s %s %s' % (minutes, ungettext('minute', 'minutes', minutes),
                                    seconds, ungettext('second', 'seconds', seconds))
        elif minutes:
            return '%s %s' % (minutes, ungettext('minute', 'minutes', minutes))
        elif seconds:
            return '%s %s' % (seconds, ungettext('second', 'seconds', seconds))
    elif fmt == 'hm':
        return '%s:%02d' % (total_hours, minutes)
    elif fmt == 'HM':
        if total_hours and minutes:
            return '%s %s %s %s' % (total_hours, ungettext('hour', 'hours', total_hours),
                                    minutes, ungettext('minute', 'minutes', minutes))
        elif total_hours:
            return '%s %s' % (total_hours, ungettext('hour', 'hours', total_hours))
        elif minutes:
            return '%s %s' % (minutes, ungettext('minute', 'minutes', minutes))
    elif fmt == 'h':
        return '%s' % total_hours
    elif fmt == 'H':
        return '%s %s' % (total_hours, ungettext('hour', 'hours', total_hours))
    elif fmt == 'DH':
        if total_hours >= 1:
            total_days, hours = divmod(total_hours, 24)
            if total_days and hours:
                return '%s %s %s %s' % (total_days, ungettext('day', 'days', total_days),
                                        hours, ungettext('hour', 'hours', hours))
            elif total_days:
                return '%s %s' % (total_days, ungettext('day', 'days', total_days))
            elif hours:
                return '%s %s' % (hours, ungettext('hour', 'hours', hours))
        else:
            return seconds_to_time(total_seconds, 'HM')
