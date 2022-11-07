import logging

import dramatiq
from context_logging import Context, current_context

from .crawler import Crawler
from .models import Run

logger = logging.getLogger(__name__)


@dramatiq.actor(max_retries=1, store_results=True)
@Context()
def run_crawler_task(run_id: int, url: str, depth: int = 0):
    """
    TODO: status = error - когда ставим?
    """

    self: dramatiq.Message = dramatiq.middleware.CurrentMessage.get_current_message()
    current_context["message_id"] = self.message_id
    current_context["url"] = url
    current_context["run_id"] = run_id
    current_context["depth"] = depth

    run = Run.objects.get(id=run_id)
    current_context["run"] = run

    crawler = Crawler(run, url, depth)
    urls_to_crawl = crawler.crawl_url_and_get_next_urls_to_crawl()

    if not urls_to_crawl:
        return

    logger.debug("continue crawling...")

    logger.debug(f"{urls_to_crawl=}")
    for index, url in enumerate(urls_to_crawl, start=1):
        next_depth = depth + 1
        logger.debug(f"({index})/({len(urls_to_crawl)}) sending 'run_crawler_task' for {url=}, {next_depth=}...")
        run_crawler_task.send(run_id, url, next_depth)
