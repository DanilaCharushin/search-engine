import logging

import dramatiq
import requests
from context_logging import Context, current_context

from .models import Link, LinkWord, Run, Url, UrlWord, Word
from .parser import Parser

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

    logger.debug(f"processing {url}...")

    try:
        Url.objects.get(value=url, is_crawled=True)
    except Url.DoesNotExist:
        logger.debug("crawled url not found in db, it will be processed")
    else:
        logger.warning("crawled url found in db, skip it")
        return

    logger.debug("sending request...")
    try:
        response = requests.get(url)
    except requests.exceptions.SSLError as exc:
        logger.warning(f"skip url due to {exc}")
        return

    logger.debug(f"{response=}")

    text = response.text
    if not text:
        logger.debug("Empty text in response!")
        return

    logger.debug("parsing elements from text...")
    elements = Parser.construct_search_elements_from_text(text)
    logger.debug(f"{len(elements)=}")

    urls_to_create = []
    words_to_create = []
    for element in elements:
        urls_to_create.append(Url(value=element.href))
        words_to_create.append(Word(value=element.word))

    logger.debug(f"get_or_create url object (value={url})...")
    created_url, created = Url.objects.get_or_create(value=url)
    logger.debug(f"{created_url=}, {created=}")

    logger.debug("creating urls from elements...")
    Url.objects.bulk_create(urls_to_create, ignore_conflicts=True)

    logger.debug("creating words from elements...")
    Word.objects.bulk_create(words_to_create, ignore_conflicts=True)

    links = []
    url_words = []
    for element in elements:
        _url = Url.objects.get(value=element.href)
        element.url_id = _url.id
        links.append(Link(url_from=created_url, url_to=_url))

        _word = Word.objects.get(value=element.word)
        element.word_id = _word.id
        url_words.append(UrlWord(url=created_url, word=_word, location=element.location))

    logger.debug("creating links from elements...")
    Link.objects.bulk_create(links, ignore_conflicts=True)

    logger.debug("creating url_word from elements...")
    UrlWord.objects.bulk_create(url_words, ignore_conflicts=True)

    link_words = []
    for element in elements:
        link_words.append(
            LinkWord(
                link=Link.objects.get(url_from=created_url, url_to_id=element.url_id),
                word_id=element.word_id,
            ),
        )

    logger.debug("creating link_word from elements...")
    LinkWord.objects.bulk_create(link_words, ignore_conflicts=True)

    created_url.is_crawled = True
    created_url.save()

    logger.debug("finishing crawling...")

    run = Run.objects.get(id=run_id)

    try:
        run.urls.add(created_url)
    except Exception as exc:
        logger.warning(exc)
    else:
        logger.debug("url added to run urls")

    if run.depth <= depth:
        logger.info("STOP CRAWLING, DEPTH REACHED!")
        run.finish()
        return

    logger.debug("continue crawling...")

    # sending next urls
    crawled_urls = list(Url.objects.filter(is_crawled=True).values_list("value", flat=True))
    urls_to_crawl = [element.href for element in elements if element.href not in crawled_urls]

    logger.debug(f"{urls_to_crawl=}")
    for index, url in enumerate(urls_to_crawl, start=1):
        next_depth = depth + 1
        logger.debug(f"({index})/({len(urls_to_crawl)}) sending 'run_crawler_task' for {url=}, {next_depth=}...")
        run_crawler_task.send(run_id, url, next_depth)
