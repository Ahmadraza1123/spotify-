from rest_framework import serializers
from .models import Library
from songs.serializers import SongSerializer

class LibrarySerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Library
        fields = ["id", "songs"]
