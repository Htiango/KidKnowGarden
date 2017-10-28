from django.db import models
from django.contrib.auth.models import User


# User's profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="Empty...", max_length=300, blank=True)
    avatar = models.ImageField(upload_to="avatar_img/", default='avatar_img/default.png', blank=True)
    # K-12 Grade, 0 for kindergarten, 1 for first grade, 9 for 9th grade and so on
    grade = models.IntegerField(default=0)
    friends = models.ManyToManyField(User, related_name="friends", blank=True)

    # Information on global scoreboard, display in user's profile is optional.
    score = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

    # Stats for each user
    # stats = models.ManyToManyField(UserStats, related_name="user_stats", blank=True)

    def __str__(self):
        return self.bio