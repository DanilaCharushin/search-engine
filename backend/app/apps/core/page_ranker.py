import logging
from typing import Dict, List

from .entities import PageRankURL, ResultURL, UrlDistance
from .models import Link, PageRank, Url, UrlWord, Word

logger = logging.getLogger(__name__)


class PageRanker:
    @classmethod
    def distance_score(cls, words: List[str]) -> List[UrlDistance]:
        try:
            combinations = UrlWord.get_words_locations_combinations(words)
        except Word.DoesNotExist:
            return []

        if not combinations:
            return []

        min_distance_list = list({UrlDistance(combination.url_id, 999999.9) for combination in combinations})

        for url_distance in min_distance_list:
            for combination in combinations:
                if combination.url_id != url_distance.url_id:
                    continue

                distance = 0
                for i in range(len(combination.word_locations) - 1):
                    distance += abs(combination.word_locations[i + 1] - combination.word_locations[i])
                url_distance.distance = min(url_distance.distance, distance)

        return cls.normalized_score(min_distance_list)

    @staticmethod
    def normalized_score(url_distances: List[UrlDistance], is_small_better=True) -> List[UrlDistance]:
        min_score = min(url_distances, key=lambda ud: ud.distance).distance
        max_score = max(url_distances, key=lambda ud: ud.distance).distance

        if is_small_better:
            for url_distance in url_distances:
                url_distance.distance = float(min_score) / url_distance.distance
        else:
            for url_distance in url_distances:
                url_distance.distance = float(url_distance.distance) / max_score

        return url_distances

    @staticmethod
    def calculate_ranks(iterations_count=25, d_coefficient=0.85) -> List[PageRank]:
        logger.info("Start calculating page ranks ...")

        page_ranks: Dict[int, PageRankURL] = {}

        for url_id in set(Url.objects.values_list("id", flat=True)):
            links_count = Link.objects.filter(url_from_id=url_id).count()
            references = list(Link.objects.filter(url_to_id=url_id).values_list("url_from_id", flat=True))
            page_ranks.setdefault(
                url_id,
                PageRankURL(
                    url_id=url_id,
                    links_count=links_count,
                    rank=1.0,
                    ratio=1.0 / links_count if links_count else 1.0,
                    references=references,
                ),
            )

        for _ in range(iterations_count):
            for page in page_ranks.values():
                other_links_sum = 0
                for ref in page.references:
                    other_links_sum += page_ranks.get(ref).ratio

                page.rank = (1 - d_coefficient) + d_coefficient * other_links_sum
                page.ratio = page.rank / page.links_count if page.links_count else page.rank

        PageRank.objects.all().delete()
        PageRank.objects.bulk_create(
            [PageRank(value=page_rank.rank, url_id=page_rank.url_id) for page_rank in page_ranks.values()],
        )

        logger.info("pages ranks CALCULATED!")

        return PageRank.objects.select_related("url").order_by("-value")

    @staticmethod
    def get_normalized_page_ranks_by_result_urls(urls: List[ResultURL]) -> List[ResultURL]:
        urls_dict = {url.url_id: url for url in urls}
        logger.debug(f"{urls_dict=}")

        urls_with_page_rank = [
            ResultURL(
                url_id=page_rank.url.id,
                url_value=page_rank.url.value,
                page_rank_raw_metric=page_rank.value,
            )
            for page_rank in PageRank.objects.select_related("url").filter(url_id__in=urls_dict)
        ]
        logger.debug(f"{urls_with_page_rank=}")

        if not urls_with_page_rank:
            return []

        max_rank = max(urls_with_page_rank, key=lambda url: url.page_rank_raw_metric).page_rank_raw_metric
        ratio = 1 / max_rank
        for url in urls_with_page_rank:
            url.page_rank_normalized_metric = url.page_rank_raw_metric * ratio
            url.distance_normalized_metric = urls_dict[url.url_id].distance_normalized_metric
            url.total_rating = (url.page_rank_normalized_metric * url.distance_normalized_metric) / (
                url.page_rank_normalized_metric + url.distance_normalized_metric
            )

        return urls_with_page_rank
