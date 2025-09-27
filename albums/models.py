from django.db import models
from users.models import User

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    release_date = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to="albums/covers/", blank=True)

    @property
    def total_likes(self):

        return sum(song.liked_by.count() for song in self.songs.all())

    @property
    def total_dislikes(self):

        return sum(song.disliked_by.count() for song in self.songs.all())

    class Meta:
        unique_together = ('artist', 'title')
