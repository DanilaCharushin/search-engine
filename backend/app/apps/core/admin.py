from django.contrib import admin
from django.contrib.admin import ModelAdmin

from . import models


@admin.register(models.Word)
class WordAdmin(ModelAdmin):
    list_display = ("value", "is_filtered")
    list_filter = ("is_filtered",)
    search_fields = ("value",)


@admin.register(models.Url)
class UrlAdmin(ModelAdmin):
    list_display = ("value", "is_crawled")
    list_filter = ("is_crawled",)
    search_fields = ("value",)


@admin.register(models.UrlWord)
class UrlWordAdmin(ModelAdmin):
    list_display = ("id", "location", "url", "word")
    search_fields = ("location", "url__value", "word__value")


@admin.register(models.Link)
class LinkAdmin(ModelAdmin):
    list_display = ("id", "url_from", "url_to")
    search_fields = ("url_from__value", "url_to__value")


@admin.register(models.LinkWord)
class LinkWordAdmin(ModelAdmin):
    list_display = ("id", "link", "word")
    search_fields = ("link__url_from__value", "link__url_to__value", "word__value")


@admin.register(models.PageRank)
class PageRankAdmin(ModelAdmin):
    pass


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
