from django.conf import settings
from django.core.management.base import BaseCommand
import filelock

from stats import stats_whore
from stats.logger import logger


class Command(BaseCommand):

    def handle(self, *args, **options):
        lock = filelock.FileLock(str(settings.BASE_DIR.parent.joinpath('file.lock')), timeout=5)
        # TODO добавить обработку остановки по ctr+c и т.п.
        with lock:
            try:
                stats_whore.main()
            except Exception:
                logger.exception('unexpected error')
                raise
