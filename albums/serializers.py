from rest_framework import serializers
from .models import Album

class AlbumSerializer(serializers.ModelSerializer):
    Album_id = serializers.IntegerField(source="id", read_only=True)
    Album_name = serializers.CharField(source="title")
    artist_id = serializers.IntegerField(source="artist.id", read_only=True)
    artist_name = serializers.CharField(source="artist.username", read_only=True)
    song_count = serializers.IntegerField(source="songs.count", read_only=True)
    cover_image = serializers.ImageField(required=False, use_url=True)
    total_likes = serializers.IntegerField(read_only=True)
    total_dislikes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Album
        fields = [
            "Album_id",
            "Album_name",
            "artist_id",
            "artist_name",
            "song_count",
            "cover_image",
            "total_likes",
            "total_dislikes",
        ]
