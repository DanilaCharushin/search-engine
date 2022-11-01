from context_logging import setup_log_record

from .base import *  # noqa

LOG_DATABASE = False

LOG_REQUESTS = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"},
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] [PID %(process)d] [THRD %(thread)d] [%(request_id)s] "
            "[%(pathname)s:%(funcName)s:%(lineno)s] [%(levelname)s] %(message)s --- %(context)s",
        },
        "simple": {"format": "[%(asctime)s] [%(request_id)s] [%(levelname)s] %(message)s"},
        "sql": {"format": "[%(asctime)s] [%(request_id)s] %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["request_id"],
        },
        "console_simple": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["request_id"],
        },
        "console_sql": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "sql",
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "app.apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "log_request_id.middleware": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

DJANGO_DB_LOGGING = {
    "handlers": ["console_sql"],
    "level": "DEBUG",
    "propagate": True,
}

LOG_DATABASE and LOGGING["loggers"].update({"django.db": DJANGO_DB_LOGGING})

setup_log_record()
