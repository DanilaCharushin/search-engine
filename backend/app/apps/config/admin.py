from django.contrib import admin

from .models import Config


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    list_editable = ("value",)
    search_fields = ("key", "value")
