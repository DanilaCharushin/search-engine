from context_logging import setup_log_record

from .base import *  # noqa

DEBUG = False

DATABASES["default"]["ENGINE"].replace("django.db.backends", "django_prometheus.db.backends")

SECURE_SSL_REDIRECT = False

SECURE_REDIRECT_EXEMPT = [r"^metrics$"]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True

LOG_REQUESTS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
        "request_id": {"()": "log_request_id.filters.RequestIDFilter"},
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] [PID %(process)d] [%(request_id)s] [%(pathname)s:%(funcName)s:%(lineno)s] "
            "[%(levelname)s] %(message)s --- %(context)s",
        },
        "simple": {"format": "[%(asctime)s] [%(request_id)s] [%(levelname)s] %(message)s"},
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
    },
    "loggers": {
        "app.apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "log_request_id.middleware": {
            "handlers": ["console_simple"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

setup_log_record()
