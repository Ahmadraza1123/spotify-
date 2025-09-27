from rest_framework import viewsets, permissions,filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Song
from .serializers import SongSerializer

class SongViewSet(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'song_name',
        'album__title',
        'album__artist__username',
    ]





    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, "role", None) == "singer":
            return Song.objects.filter(album__artist=user)
        return Song.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "singer":
            raise PermissionDenied("Only singers can upload songs.")
        album = serializer.validated_data.get("album")
        if album.artist != user:
            raise PermissionDenied("You can only add songs to your own albums.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        song = self.get_object()
        if getattr(user, "role", None) == "singer" and song.album.artist != user:
            raise PermissionDenied("You can only update your own songs.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if getattr(user, "role", None) == "singer" and instance.album.artist != user:
            raise PermissionDenied("You can only delete your own songs.")
        instance.delete()

    @action(detail=True, methods=["post"], url_path="like")
    def like_song(self, request, pk=None):
        song = self.get_object()
        user = request.user

        if getattr(user, "role", None) == "singer":
            return Response({"error": "Singers cannot like songs."}, status=403)


        if song.liked_by.filter(id=user.id).exists():
            song.liked_by.remove(user)
            return Response({
                "message": "Like removed",
                "total_likes": song.total_likes,
                "total_dislikes": song.total_dislikes
            })



        song.liked_by.add(user)
        return Response({
            "message": "Song liked",
            "total_likes": song.total_likes,
            "total_dislikes": song.total_dislikes
        })

    @action(detail=True, methods=["post"], url_path="dislike")
    def dislike_song(self, request, pk=None):
        song = self.get_object()
        user = request.user

        if getattr(user, "role", None) == "singer":
            return Response({"error": "Singers cannot dislike songs."}, status=403)


        if song.disliked_by.filter(id=user.id).exists():
            song.disliked_by.remove(user)
            return Response({
                "message": "Dislike removed",
                "total_likes": song.total_likes,
                "total_dislikes": song.total_dislikes
            })


        if song.liked_by.filter(id=user.id).exists():
            song.liked_by.remove(user)


        song.disliked_by.add(user)
        return Response({
            "message": "Song disliked",
            "total_likes": song.total_likes,
            "total_dislikes": song.total_dislikes
        })
