from django.urls import path
from . import views
from .views import FollowArtistView, UnfollowArtistView

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset-confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),

    path('follow/', FollowArtistView.as_view(), name='follow-artist'),

    path('unfollow/', UnfollowArtistView.as_view(), name='unfollow-artist'),
]
