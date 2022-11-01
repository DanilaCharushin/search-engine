from typing import List, Tuple

import dramatiq
from apscheduler.triggers.cron import CronTrigger

ActorPath = str
ActorName = str

JOBS: List[Tuple[CronTrigger, ActorPath, ActorName]] = []


def cron(crontab: str) -> callable:
    """Wraps a Dramatiq actor in a cron schedule."""

    def decorator(actor: dramatiq.Actor):
        JOBS.append((CronTrigger.from_crontab(crontab), actor.fn.__module__, actor.fn.__name__))
        return actor

    return decorator
