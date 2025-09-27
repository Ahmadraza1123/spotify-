from django.db import models
from albums.models import Album
from django.conf import settings



class Song(models.Model):
    title = models.CharField(max_length=255)
    duration = models.DurationField(null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="songs")
    cover_image = models.ImageField(upload_to="albums/covers/", null=True, blank=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_songs", blank=True)
    disliked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="disliked_songs", blank=True)

    @property
    def total_likes(self):
        return self.liked_by.count()

    @property
    def total_dislikes(self):
        return self.disliked_by.count()

    class Meta:
        unique_together = ('album', 'title')
