from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ArtistSerializer,
    AlbumSerializer
)
from albums.models import Album


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = get_random_string(length=32)
        user.email_verification_token = token
        user.save()

        verify_link = f"http://127.0.0.1:8000/users/verify-email/?token={token}"

        send_mail(
            "Verify Your Email - Spotify Clone ",
            f"Hello {user.username},\n\nPlease verify your email by clicking this link:\n{verify_link}\n\nThanks!",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "User registered successfully. Verification email sent."},
            status=status.HTTP_201_CREATED,
        )


class LoginView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.id, "username": user.username, "email": user.email})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully."})


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            token = get_random_string(length=32)
            user.password_reset_token = token
            user.password_reset_token_created_at = timezone.now()
            user.save()

            reset_link = f"http://localhost:8000/users/password-reset-confirm/?token={token}"
            send_mail(
                "Password Reset",
                f"Click this link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"message": "Password reset email sent"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")
        if not token or not new_password:
            return Response({"error": "Token and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(password_reset_token=token)
            if user.password_reset_token_created_at is None or timezone.now() > user.password_reset_token_created_at + timedelta(hours=1):
                return Response({"error": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.password_reset_token = ""
            user.password_reset_token_created_at = None
            user.save()

            send_mail(
                "Password Changed Successfully",
                "Your password has been changed successfully.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "Password reset successful"})
        except User.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.GET.get("token")
        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True
            user.email_verification_token = ""
            user.save()
            return Response({"message": "Email verified successfully!"})
        except User.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class FollowArtistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != "normal":
            return Response({"error": "Only normal users can follow artists"}, status=403)

        artist_id = request.data.get("artist_id")
        try:
            artist = User.objects.get(id=artist_id, role="singer")
        except User.DoesNotExist:
            return Response({"message": f"You followed {artist.username}"})

        user.following.add(artist)
        user.unfollowed.remove(artist)
        return Response({"message": f"You followed {artist.username}"})


class UnfollowArtistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != "normal":
            return Response({"error": "Only normal users can unfollow artists"}, status=403)

        artist_id = request.data.get("artist_id")
        try:
            artist = User.objects.get(id=artist_id, role="singer")
        except User.DoesNotExist:
            return Response({"error": "Artist not found"}, status=404)

        user.following.remove(artist)
        user.unfollowed.add(artist)
        return Response({"message": f"You unfollowed {artist.username}"})

class SearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get("q", "")
        if not query:
            return Response({"error": "Query parameter 'q' is required"}, status=400)

        # Search Artists (singers only)
        artists = User.objects.filter(role="Singer", Artist__icontains=query)
        artist_data = ArtistSerializer(artists, many=True).data

        # Search Albums
        albums = Album.objects.filter(title__icontains=query)
        album_data = AlbumSerializer(albums, many=True).data

        # Search Songs
        songs = Song.objects.filter(title__icontains=query)
        song_data = SongSerializer(songs, many=True).data

        return Response({
            "artists": artist_data,
            "albums": album_data,
            "songs": song_data
        })
