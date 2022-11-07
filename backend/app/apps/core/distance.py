import logging
from typing import List

from .entities import ResultURL, UrlDistance
from .models import Word
from .page_ranker import PageRanker
from .searcher import Searcher

logger = logging.getLogger(__name__)


class SearchProvider:
    @staticmethod
    def search(query: str, max_urls_count=5) -> str:
        search_words = query.split(" ")
        if len(search_words) < 2:
            return ""

        distanced_urls = PageRanker.distance_score(search_words)
        if not distanced_urls:
            return ""

        distanced_urls: List[UrlDistance] = sorted(distanced_urls, key=lambda ud: ud.distance, reverse=True)
        logger.debug(f"{distanced_urls=}")
        result_urls = [
            ResultURL(
                url_id=element.url_id,
                distance_normalized_metric=element.distance,
            )
            for element in distanced_urls
        ]

        result_urls = PageRanker.get_normalized_page_ranks_by_result_urls(result_urls)
        if not result_urls:
            return ""

        result_urls = sorted(result_urls, key=lambda u: u.total_rating, reverse=True)
        logger.debug(f"{result_urls=}")

        result = ""
        max_urls_count = min(max_urls_count, len(distanced_urls))
        for url in result_urls[:max_urls_count]:
            words = list(
                Word.objects.filter(urlword__url_id=url.url_id)
                .values_list("value", flat=True)
                .order_by("urlword__location"),
            )
            result += Searcher.create_marked_html(url, words, search_words)

        return result
