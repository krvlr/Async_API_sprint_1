"""Конфигурация для логгера."""

import os


LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': os.environ.get('LOGGING_LEVEL'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'level': os.environ.get('LOGGING_LEVEL'),
            'handlers': ['console'],
            'propagate': True,
        }
    },
}
