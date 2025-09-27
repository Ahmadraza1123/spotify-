from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('library/', include('library.urls')),

    path('albums/', include('albums.urls')),
    path('songs/', include('songs.urls')),
]