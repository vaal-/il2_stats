from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class StatsConfig(AppConfig):
    name = 'stats'
    verbose_name = _('Stats')

    def ready(self):
        import stats.signals.handlers
        # import stats.signals.signals
