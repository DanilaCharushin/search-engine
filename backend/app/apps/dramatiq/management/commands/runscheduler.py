import logging
import signal
from typing import Dict

from apscheduler.job import Job
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore

from app.apps.dramatiq.jobs import JOBS

logger = logging.getLogger(__name__)

JobID = str


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("Setting up scheduler...")

        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        store = DjangoJobStore()
        scheduler.add_jobstore(store)

        logger.info("Importing jobs...")

        existing_jobs_map: Dict[JobID, Job] = {job.id: job for job in store.get_all_jobs()}

        logger.info("Collecting jobs...")
        for trigger, module_path, func_name in JOBS:
            job_path = f"{module_path}:{func_name}.send"
            job_name = f"{module_path}.{func_name}"

            if job_name in existing_jobs_map:
                logger.info(f'Job "{job_name}" already exists in store, checking its trigger...')

                existing_job = existing_jobs_map[job_name]
                if str(existing_job.trigger) != str(trigger):
                    logger.info(f'Trigger for job "{job_name}" CHANGED! Updating job...')
                    existing_job.trigger = trigger
                    store.update_job(existing_job)
                else:
                    logger.info(f'Trigger for job "{job_name}" not changed, skipping job...')
            else:
                logger.info(f'ADDING job "{job_name}" to store...')
                scheduler.add_job(job_path, trigger=trigger, name=job_name, id=job_name)

        def shutdown(signum, frame):
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        logger.info("Starting scheduler...")
        scheduler.start()
