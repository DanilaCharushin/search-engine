import logging
import random  # noqa
from typing import List

from airium import Airium
from django.urls import reverse
from django.utils.safestring import mark_safe

from .entities import ResultURL

logger = logging.getLogger(__name__)


class Searcher:
    @staticmethod
    def create_marked_html(url: ResultURL, words: List[str], marked_words: List[str]) -> str:
        marked_set = {}
        for word in marked_words:
            rand_color = "%06x" % random.randint(0, 0xFFFFFF)  # noqa
            marked_set[word] = rand_color

        doc_gen = Airium(source_minify=True)

        with doc_gen.html("lang=ru"):
            with doc_gen.head():
                doc_gen.meta(charset="utf-8")
                doc_gen.title(_t="Marked Words Test")

            with doc_gen.body():
                with doc_gen.p():
                    with doc_gen.p():
                        link_to_url_in_admin = mark_safe(
                            f'<a href="{reverse("admin:core_url_change", args=(url.url_id,))}" target="_blank">'
                            f"{url.url_id}</a>",
                        )
                        link_to_site = mark_safe(f'<a href="{url.url_value}" target="_blank">{url.url_value}</a>')
                        doc_gen(
                            f"{link_to_site} ("
                            f"id={link_to_url_in_admin}, "
                            f"total_rating={url.total_rating}, "
                            f"page_rank_raw_metric={url.page_rank_raw_metric:.3f}, "
                            f"page_rank_normalized_metric={url.page_rank_normalized_metric:.3f}, "
                            f"distance_raw_metric={url.distance_raw_metric:.3f}, "
                            f"distance_normalized_metric={url.distance_normalized_metric:.3f}"
                            f")",
                        )
                    for word in words:
                        if word not in marked_words:
                            doc_gen(word)
                        else:
                            with doc_gen.span(style=f"background-color:#{marked_set[word]}"):
                                doc_gen(word)
                        doc_gen(" ")

        return str(doc_gen)
