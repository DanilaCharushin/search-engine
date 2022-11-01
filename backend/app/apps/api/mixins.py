from typing import Dict, Literal

from rest_framework import serializers

ACTION = Literal["create", "retrieve", "update", "partial_update", "destroy", "list"]


class SerializerClassMappingMixin:
    action: ACTION
    serializer_class: serializers.Serializer
    serializer_class_mapping: Dict[ACTION, serializers.Serializer]

    def get_serializer_class(self):
        return self.serializer_class_mapping.get(self.action, self.serializer_class)
