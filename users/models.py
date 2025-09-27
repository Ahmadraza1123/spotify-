from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):

    email = models.EmailField(unique=True)
    email_verification_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_token_created_at = models.DateTimeField(blank=True, null=True)

    ROLE_CHOICES = (
        ('normal', 'Normal'),
        ('singer', 'Singer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')


    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )
    unfollowed = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="unfollowed_by",
        blank=True
    )

    def is_reset_token_expired(self):
        if self.password_reset_token_created_at:
            return timezone.now() > self.password_reset_token_created_at + timedelta(hours=1)
        return True




