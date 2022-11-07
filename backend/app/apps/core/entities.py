import dataclasses
from typing import List


@dataclasses.dataclass
class WordLocationsCombination:
    url_id: int
    word_locations: List[int]


@dataclasses.dataclass
class UrlDistance:
    url_id: int
    distance: float

    def __hash__(self):
        return self.url_id


@dataclasses.dataclass
class PageRankURL:
    url_id: int
    links_count: int
    rank: float
    ratio: float
    references: List[int]


@dataclasses.dataclass
class ResultURL:
    url_id: int = 0
    url_value: str = ""
    distance_normalized_metric: float = 0.0
    distance_raw_metric: float = 0.0
    page_rank_normalized_metric: float = 0.0
    page_rank_raw_metric: float = 0.0
    total_rating: float = 0.0
