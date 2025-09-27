from django.db import models
from users.models import User

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    release_date = models.DateField(null=True, blank=True)
    cover_image = models.ImageField(upload_to="albums/covers/", blank=True)
    followers = models.ManyToManyField(User,related_name="followed_albums", blank=True)
    unfollowers = models.ManyToManyField(User,related_name="unfollowed_albums",blank=True)

    @property
    def total_likes(self):

        return sum(song.liked_by.count() for song in self.songs.all())

    @property
    def total_dislikes(self):

        return sum(song.disliked_by.count() for song in self.songs.all())

    @property

    def total_followers(self):
        return self.followers.count()

    @property
    def total_unfollowers(self):
        return self.unfollowers.count()

    class Meta:
        unique_together = ('artist', 'title')
