import logging
import logging.config
import logging.handlers

from django.conf import settings

logger = logging.getLogger('stats')

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(message)s',
            'datefmt': '%Y.%m.%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(settings.BASE_DIR.parent.joinpath('stats.log')),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 1,
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
})
