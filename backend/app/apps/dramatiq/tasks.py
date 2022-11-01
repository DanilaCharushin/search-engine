import logging
import time

import dramatiq

logger = logging.getLogger(__name__)


@dramatiq.actor(max_retries=0, store_results=True)
def ping_task(time_to_sleep):
    logger.debug(f"Ping task with param {time_to_sleep=} start processing!")

    self: dramatiq.Message = dramatiq.middleware.CurrentMessage.get_current_message()
    logger.debug(f"{self.message_id=}")

    time.sleep(time_to_sleep)

    logger.debug(f"Ping task with param {time_to_sleep=} finished!")
    return f"Done in {time_to_sleep} seconds"
