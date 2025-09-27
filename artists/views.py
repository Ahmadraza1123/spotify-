from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Artist
from .serializers import ArtistSerializer
from .permissions import IsSinger


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = [IsAuthenticated, IsSinger]

    def perform_create(self, serializer):

        serializer.save()


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        artist = self.get_object()
        artist.followers.add(request.user)
        return Response({"message": f"You followed {artist.name}"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        artist = self.get_object()
        artist.followers.remove(request.user)
        return Response({"message": f"You unfollowed {artist.name}"})
