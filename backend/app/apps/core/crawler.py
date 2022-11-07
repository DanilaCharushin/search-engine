import dataclasses
import logging
from typing import List, Optional

import requests

from .models import Link, LinkWord, Run, Url, UrlWord, Word
from .parser import Parser

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Crawler:
    run: Run
    url: str
    depth: int

    def crawl_url_and_get_next_urls_to_crawl(self) -> Optional[List[str]]:
        logger.debug(f"processing {self.url}...")

        try:
            Url.objects.get(value=self.url, is_crawled=True)
        except Url.DoesNotExist:
            logger.debug("crawled url not found in db, it will be processed")
        else:
            if self.depth > 0:
                logger.warning("crawled url found in db, skip it")
                return None

        try:
            text = self._get_text_to_parse()
        except requests.exceptions.SSLError as exc:
            logger.warning(f"skip url due to {exc}")
            return None

        if not text:
            logger.debug("Empty text in response!")
            return None

        logger.debug("parsing elements from text...")
        elements = Parser.construct_search_elements_from_text(text)
        logger.debug(f"{len(elements)=}")

        urls_to_create = []
        words_to_create = []
        for element in elements:
            words_to_create.append(Word(value=element.word))
            element.href and urls_to_create.append(Url(value=element.href))

        logger.debug(f"get_or_create url object (value={self.url})...")
        created_url, created = Url.objects.get_or_create(value=self.url)
        logger.debug(f"{created_url=}, {created=}")

        logger.debug("creating urls from elements...")
        Url.objects.bulk_create(urls_to_create, ignore_conflicts=True)

        logger.debug("creating words from elements...")
        Word.objects.bulk_create(words_to_create, ignore_conflicts=True)

        links = []
        url_words = []
        for element in elements:
            _word = Word.objects.get(value=element.word)
            element.word_id = _word.id
            url_words.append(UrlWord(url=created_url, word=_word, location=element.location))

            if element.href:
                _url = Url.objects.get(value=element.href)
                element.url_id = _url.id
                links.append(Link(url_from=created_url, url_to=_url))

        logger.debug("creating links from elements...")
        Link.objects.bulk_create(links, ignore_conflicts=True)

        logger.debug("creating url_word from elements...")
        UrlWord.objects.bulk_create(url_words, ignore_conflicts=True)

        link_words = []
        for element in elements:
            element.url_id and link_words.append(
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

        try:
            self.run.urls.add(created_url)
        except Exception as exc:
            logger.warning(exc)
        else:
            logger.debug("url added to run urls")

        if self.run.depth <= self.depth:
            logger.info("STOP CRAWLING, DEPTH REACHED!")
            self.run.finish()
            return None

        crawled_urls = list(Url.objects.filter(is_crawled=True).values_list("value", flat=True))
        return [element.href for element in elements if element.href and element.href not in crawled_urls]

    def _get_text_to_parse(self) -> str:
        logger.debug("sending request...")
        response = requests.get(self.url)

        logger.debug(f"{response=}")
        return response.text
