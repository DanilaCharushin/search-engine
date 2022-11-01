from typing import Any

from django.db import models


class Config(models.Model):
    key = models.CharField(
        max_length=100,
        verbose_name="Ключ",
        primary_key=True,
    )
    value = models.TextField(
        verbose_name="Значение",
    )

    description = models.TextField(
        verbose_name="Описание",
        null=True,
    )

    class Meta:
        db_table = "config"
        verbose_name = "Параметр конфигурации"
        verbose_name_plural = "Конфигурация приложения"

    def __str__(self):
        return f'Параметр "{self.key}"="{self.value}'

    def __repr__(self):
        return f'<Config "{self.key}"="{self.value}>'

    @classmethod
    def __get_or_create(cls, key: str, default_value: Any, description: str) -> str:
        params = {
            "key": key,
            "defaults": {
                "value": str(default_value),
                "description": description,
            },
        }
        return cls.objects.get_or_create(**params)[0].value
