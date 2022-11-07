from django.contrib import admin
from django.contrib.admin import ModelAdmin

from . import models


@admin.register(models.Word)
class WordAdmin(ModelAdmin):
    list_display = ("value", "total_count", "link_count")
    search_fields = ("value",)
    ordering = ("id",)

    @admin.display(description="Количество упоминаний всего")
    def total_count(self, obj: models.Word) -> int:
        return models.UrlWord.objects.filter(word=obj).count()

    @admin.display(description="Количество упоминаний в ссылках")
    def link_count(self, obj: models.Word) -> int:
        return models.LinkWord.objects.filter(word=obj).count()


@admin.register(models.Url)
class UrlAdmin(ModelAdmin):
    list_display = ("value", "is_crawled", "rank", "from_count", "to_count")
    list_filter = ("is_crawled",)
    search_fields = ("value",)
    ordering = ("id",)

    @admin.display(description="Количество исходящих ссылок")
    def from_count(self, obj: models.Url) -> int:
        return models.Link.objects.filter(url_from=obj).count()

    @admin.display(description="Количество указывающих ссылок")
    def to_count(self, obj: models.Url) -> int:
        return models.Link.objects.filter(url_to=obj).count()

    @admin.display(description="Ранг")
    def rank(self, obj: models.Url) -> float:
        try:
            return models.PageRank.objects.filter(url=obj).first().value
        except:  # noqa
            return -1


@admin.register(models.Link)
class LinkAdmin(ModelAdmin):
    list_display = ("id", "url_from", "url_to", "to_count", "words_in_link")
    search_fields = ("url_from__value", "url_to__value")
    ordering = ("id",)

    @admin.display(description="Количество слов в ссылке")
    def to_count(self, obj: models.Link) -> int:
        return models.LinkWord.objects.filter(link=obj).count()

    @admin.display(description="Слова в ссылке")
    def words_in_link(self, obj: models.Link) -> str:
        return " ; ".join(list(models.Word.objects.filter(linkword__link=obj).values_list("value", flat=True)))


@admin.register(models.UrlWord)
class UrlWordAdmin(ModelAdmin):
    list_display = ("id", "location", "url", "word")
    search_fields = ("location", "url__value", "word__value")


@admin.register(models.LinkWord)
class LinkWordAdmin(ModelAdmin):
    list_display = ("id", "link", "word")
    search_fields = ("link__url_from__value", "link__url_to__value", "word__value")


@admin.register(models.PageRank)
class PageRankAdmin(ModelAdmin):
    list_display = ("value", "url")
    search_fields = ("value", "url")
    ordering = ("-value",)


@admin.register(models.Run)
class RunAdmin(ModelAdmin):
    list_display = ("id", "status", "raw_urls", "depth", "created_at", "finished_at", "duration")
    list_filter = ("status",)
    date_hierarchy = "created_at"

    @admin.display(description="Продолжительность[сек]")
    def duration(self, obj: models.Run) -> int:
        try:
            return (obj.finished_at - obj.created_at).seconds
        except:  # noqa
            return -1
