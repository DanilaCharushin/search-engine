import logging
import os

import dramatiq_dashboard
from django.core.wsgi import get_wsgi_application

EXCLUDED_ENDPOINTS = (
    "/metrics",
    "/ping",
)

EXCLUDED_LOGGERS = (
    "gunicorn.access",
    "log_request_id.middleware",
)


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa
        return all((record.getMessage().find(endpoint) == -1 for endpoint in EXCLUDED_ENDPOINTS))


for logger in EXCLUDED_LOGGERS:
    logging.getLogger(logger).addFilter(EndpointFilter())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

application = get_wsgi_application()

dashboard_middleware = dramatiq_dashboard.make_wsgi_middleware("/dd")  # dd - dramatiq dashboard

application = dashboard_middleware(application)
