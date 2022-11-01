import re
from typing import List

import bs4

from .models import SearchElement


class Parser:
    @classmethod
    def construct_search_elements_from_text(cls, text: str) -> List[SearchElement]:
        soup = bs4.BeautifulSoup(text, "html.parser")
        for data in soup(["style", "script", "meta", "template"]):
            data.decompose()

        return cls._merge_text_and_links(soup.find_all())

    @classmethod
    def _merge_text_and_links(cls, tags: List[bs4.Tag]) -> List[SearchElement]:
        search_elements = []

        for tag in tags:
            tag_text = tag.find(text=True, recursive=False)
            if tag_text is not None:
                href = None
                if tag.name == "a":
                    href = tag.get("href")
                    if href is not None:
                        if (
                            "mailto:" in href
                            or "tel:" in href
                            or href.endswith((".jpg", ".png", ".gif", ".jpeg", ".pdf"))
                            or not href.startswith("http")
                        ):
                            continue
                        href = href.strip("/")

                if not href:
                    continue

                for location, word in enumerate(cls._text_to_wordlist(tag_text), start=len(search_elements)):
                    search_elements.append(SearchElement(word=word, location=location, href=href))

        return search_elements

    @classmethod
    def _text_to_wordlist(cls, text: str) -> List[str]:
        """Variant 1: remove digits."""

        words = re.split("[\W\d]+", text, flags=re.UNICODE)  # noqa
        words = [word for word in words if word]
        for i, word in enumerate(words):
            words[i] = word.lower()
        return words
