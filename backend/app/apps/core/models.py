import dataclasses
import itertools
from collections import defaultdict
from typing import Dict, List

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .entities import WordLocationsCombination


@dataclasses.dataclass
class SearchElement:
    word: str
    location: int = 0
    href: str = ""

    word_id: int = 0
    url_id: int = 0


class Word(models.Model):
    value = models.TextField(unique=True)

    class Meta:
        verbose_name = "Слово"
        verbose_name_plural = "Слова"

    def __str__(self):
        return self.value


class Url(models.Model):
    value = models.TextField(unique=True)
    is_crawled = models.BooleanField(default=False, db_index=True)

    words = models.ManyToManyField(
        Word,
        through="core.UrlWord",
        related_name="urls",
    )

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"

    def __str__(self):
        return f"{self.value} (is_crawled={self.is_crawled})"


class UrlWord(models.Model):
    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    location = models.IntegerField()

    class Meta:
        verbose_name = "Ссылка <-> Слово"
        verbose_name_plural = "Ссылки <-> Слова"
        unique_together = ("url", "word", "location")

    @staticmethod
    def get_words_locations_combinations(words: List[str]) -> List[WordLocationsCombination]:
        def __check_and_fill_locations_list(_url_id: int) -> None:
            """
            `urls_ids_to_locations_map` dict looks like this (`123` is url_id):
            {
                123: [[],[],[], ...]
            }         |  |  |
                      |  |  locations for third word
                      |  locations for second word
                      locations for first word
            """
            if not urls_ids_to_locations_map[_url_id]:
                for _ in range(len(words)):
                    urls_ids_to_locations_map[_url_id].append([])

        urls_ids_to_locations_map: Dict[int, List[list]] = defaultdict(list)

        for word_index, word in enumerate(words):
            url_words = UrlWord.objects.filter(word=Word.objects.get(value=word)).order_by("location", "url_id")
            for url_word in url_words:
                __check_and_fill_locations_list(url_word.url_id)
                urls_ids_to_locations_map[url_word.url_id][word_index].append(url_word.location)

        result = []
        for url_id, locations_by_word in urls_ids_to_locations_map.items():
            if not all(locations_by_word):
                continue

            for combination in itertools.product(*locations_by_word):
                result.append(WordLocationsCombination(url_id, list(combination)))

        return result


class Link(models.Model):
    url_from = models.ForeignKey(Url, on_delete=models.CASCADE, related_name="links_from")
    url_to = models.ForeignKey(Url, on_delete=models.CASCADE, related_name="links_to")

    words = models.ManyToManyField(
        Word,
        through="core.LinkWord",
        related_name="links",
    )

    class Meta:
        verbose_name = "Связь"
        verbose_name_plural = "Связи"
        unique_together = ("url_from", "url_to")

    def __str__(self):
        return f"{self.url_from} -> {self.url_to}"


class LinkWord(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Связь <-> Слово"
        verbose_name_plural = "Связи <-> Слова"
        unique_together = ("link", "word")

    def __str__(self):
        return f"{self.link} ({self.word})"


class PageRank(models.Model):
    value = models.FloatField()
    url = models.ForeignKey(Url, on_delete=models.CASCADE, related_name="ranks")

    class Meta:
        verbose_name = "Ранг страницы"
        verbose_name_plural = "Ранги страниц"

    def __str__(self):
        return f"{self.value} ({self.url})"


class RunStatus(models.TextChoices):
    RUNNING = ("Запущен", "Запущен")
    DONE = ("Готово", "Готово")
    FAILED = ("Ошибка", "Ошибка")


class Run(models.Model):
    raw_urls = models.TextField(verbose_name="Список url для запуска (через запятую)")
    depth = models.IntegerField(verbose_name="Глубина обхода (0 - только страницу, 1 - +вложенные и т.д.)", default=1)

    status = models.CharField(max_length=50, choices=RunStatus.choices, editable=False, default=RunStatus.RUNNING)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    finished_at = models.DateTimeField(verbose_name="Дата завершения", null=True, blank=True)

    urls = models.ManyToManyField(Url, editable=False)

    class Meta:
        verbose_name = "Запуск"
        verbose_name_plural = "Запуски"

    def __str__(self):
        return f"Запуск {self.id} ({self.status})"

    @property
    def raw_urls_as_list(self) -> List[str]:
        return self.raw_urls.split(",")

    def finish(self):
        self.finished_at = now()
        self.status = RunStatus.DONE
        self.save()


@receiver(post_save, sender=Run)
def send_crawler_task(sender: type, instance: Run, created: bool, **kwargs):
    if created:
        from .tasks import run_crawler_task

        for url in instance.raw_urls_as_list:
            run_crawler_task.send(instance.id, url)
