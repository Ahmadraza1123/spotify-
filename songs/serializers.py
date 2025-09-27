from rest_framework import serializers
from .models import Song
from drf_extra_fields.fields import Base64ImageField


class SongSerializer(serializers.ModelSerializer):
    song_name = serializers.CharField(source="title")
    album_name = serializers.CharField(source="album.title", read_only=True)
    cover_image = Base64ImageField(source="album.cover_image", read_only=True)
    total_likes = serializers.IntegerField(read_only=True)
    total_dislikes = serializers.IntegerField(read_only=True)
    class Meta:
        model = Song
        fields = [
            "id",
            "song_name",
            "duration",
            "album",
            "album_name",
            "cover_image",
            "total_likes",
            "total_dislikes",
        ]
