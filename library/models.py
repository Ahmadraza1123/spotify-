from django.db import models
from django.conf import settings
from songs.models import Song

class Library(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="library")
    songs = models.ManyToManyField(Song, related_name="in_libraries", blank=True)


