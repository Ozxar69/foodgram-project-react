from rest_framework import serializers

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('colour', 'name', 'slug')
        read_only_fields = ('colour', 'name', 'slug')
