from rest_framework import viewsets, permissions,filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Album
from .serializers import AlbumSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "album__title", "album__artist__name"]

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

    @action(detail=True, methods=["post"], url_path="follow")
    def follow_album(self, request, pk=None):
        user = request.user
        album = self.get_object()

        if user.role != "normal":
            return Response({"error": "Only normal users can follow albums"}, status=403)

        album.followers.add(user)
        album.unfollowers.remove(user)

        return Response({
            "message": f"You followed album {album.title}",
            "total_followers": album.total_followers
        })


    @action(detail=True, methods=["post"], url_path="unfollow")
    def unfollow_album(self, request, pk=None):
        user = request.user
        album = self.get_object()

        if user.role != "normal":
            return Response({"error": "Only normal users can unfollow albums"}, status=403)

        album.followers.remove(user)
        album.unfollowers.add(user)

        return Response({
            "message": f"You unfollowed album {album.title}",
            "total_unfollowers": album.total_unfollowers
        })