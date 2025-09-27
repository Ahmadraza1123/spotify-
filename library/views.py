from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Library
from .serializers import LibrarySerializer
from songs.models import Song
from songs.serializers import SongSerializer


class LibraryViewSet(viewsets.ModelViewSet):
    serializer_class = LibrarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Library.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=False, methods=["post"], url_path="save-song")
    def save_song(self, request):
        user = request.user
        song_id = request.data.get("song_id")

        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": "Song not found."}, status=status.HTTP_404_NOT_FOUND)

        if getattr(user, "role", None) == "singer":
            return Response({"error": "Singers cannot save songs."}, status=status.HTTP_403_FORBIDDEN)

        library, _ = Library.objects.get_or_create(user=user)

        if library.songs.filter(id=song.id).exists():
            return Response({"error": f"'{song.title}' is already in your library."}, status=status.HTTP_400_BAD_REQUEST)

        library.songs.add(song)

        return Response({
            "message": f"'{song.title}' added to your library.",
            "song": SongSerializer(song).data
        }, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=["post"], url_path="remove-song")
    def remove_song(self, request):
        user = request.user
        song_id = request.data.get("song_id")

        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": "Song not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            library = Library.objects.get(user=user)
        except Library.DoesNotExist:
            return Response({"error": "You don't have a library yet."}, status=status.HTTP_404_NOT_FOUND)

        if not library.songs.filter(id=song.id).exists():
            return Response({"error": f"'{song.title}' is not in your library."}, status=status.HTTP_400_BAD_REQUEST)

        library.songs.remove(song)

        return Response({
            "message": f"'{song.title}' removed from your library."
        }, status=status.HTTP_200_OK)


