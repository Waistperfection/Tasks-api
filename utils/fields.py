from rest_framework import serializers
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter


class PassedTimeField(serializers.DateTimeField):
    def __init__(self, **kwargs):
        kwargs["format"] = None
        super().__init__(**kwargs)

    def to_representation(self, value):
        if not value:
            return "Не указана"
        return NaturalTimeFormatter.string_for(value)
