from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from channels import Group
import json


class LoggedInUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user')


class Rooms(models.Model):
    """
    A room for people to exchange information.
    """
    # Room title
    title = models.CharField(max_length=255)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("room-%s" % self.id)

    def send_message(self, message, user, random_room):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'room': str(self.id), 'message': message, 'username': user.username, 'question': random_room}

        # Send out the message to everyone in the room
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )

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


class Question(models.Model):
    content = models.TextField(default="", max_length=200)
    choice1 = models.TextField(default="", max_length=100)
    choice2 = models.TextField(default="", max_length=100)
    choice3 = models.TextField(default="", max_length=100)
    answer = models.TextField(default="", max_length=100)

    def __str__(self):
        return self.content


class CorrectAnswer(models.Model):
    answer_index = models.IntegerField(validators=[
            MaxValueValidator(3),
            MinValueValidator(0)
        ])