from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Album
from .serializers import AlbumSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:

            return Album.objects.all()

        if hasattr(user, "role") and user.role == "singer":

            return Album.objects.filter(artist=user)


        return Album.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "role") or user.role != "singer":
            raise PermissionDenied("Only singers can create albums.")
        serializer.save(artist=user)

    def perform_update(self, serializer):
        user = self.request.user
        album = self.get_object()
        if user != album.artist:
            raise PermissionDenied("You can only update your own albums.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user != instance.artist:
            raise PermissionDenied("You can only delete your own albums.")
        instance.delete()

    @action(detail=False, methods=["get"], url_path="summary")
    def singer_albums_summary(self, request):
        user = request.user
        if not user.is_authenticated or getattr(user, "role", None) != "singer":
            raise PermissionDenied("Only singers can view album summaries.")

        albums = Album.objects.filter(artist=user).order_by("-id")[:5]
        serializer = self.get_serializer(albums, many=True)

        total_likes = albums.aggregate(total=Sum("songs__likes"))["total"] or 0
        total_dislikes = albums.aggregate(total=Sum("songs__dislikes"))["total"] or 0

        return Response({
            "albums": serializer.data,
            "summary": {
                "total_likes": total_likes,
                "total_dislikes": total_dislikes
            }
        })
