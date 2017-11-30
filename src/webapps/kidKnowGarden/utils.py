from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from .exception import ClientError
from .models import *

from django.core.cache import cache

import random

def catch_client_error(func):
    """
    Decorator to catch the ClientError exception and translate it into a reply.
    """
    @wraps(func)
    def inner(message, args, **kwargs):
        try:
            return func(message, args, **kwargs)
        except ClientError as e:
            # If we catch a client error, tell it to send an error string
            # back to the client on their reply channel
            e.send_to(message.reply_channel)
    return inner


def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    if not user.is_authenticated():
        raise ClientError("USER_HAS_TO_LOGIN")
    # Find the room they requested (by ID)
    try:
        room = Rooms.objects.get(pk=room_id)
    except Rooms.DoesNotExist:
        raise ClientError("ROOM_INVALID")
    # Check permissions
    if room.staff_only and not user.is_staff:
        raise ClientError("ROOM_ACCESS_DENIED")
    return room


def is_in_another_room(user):
    # Performance will be largely affected!!!
    room_profile = Room_Profile.objects.get(user=user)
    if room_profile.inroom is not None:
        return True
    else:
        return False

def get_random_question(room):
    question = Question.objects.order_by('?')
    answered_questions_number = room.answered_questions.count()
    if answered_questions_number > 2:
        return "Contest End"
    answered_questions_id = room.answered_questions.all().values('id')
    question_to_pick = question.exclude(id__in=answered_questions_id)
    q = question_to_pick.first()
    if q is not None:
        # Shuffle choice and answers
        room.answered_questions.add(q)
        ls = [q.choice1, q.choice2, q.choice3, q.answer]
        random.shuffle(ls)
        index = ls.index(q.answer)
        new_record = CorrectAnswer(answer_index=index)
        new_record.save()
        question_string = ls[0] + "#" + ls[1] + "#" + ls[2] + "#" + ls[3] + "#" + q.content + "#" + str(new_record.id)
        return question_string
    else:
        return "Contest End"


def judge_question_correctness(record_id, answer_index):
    correct_answer = CorrectAnswer.objects.get(id=record_id)
    status = (correct_answer.answer_index == answer_index)
    return status


def save_contest_score(score, user):
    try:
        contest_score = ContestScore.objects.get(user=user)
        if ContestScore.objects.all().filter(pk=contest_score.pk).exists():
            new_score = contest_score.score + score
            contest_score.score = new_score
            contest_score.save()
    except ObjectDoesNotExist:
    # A good performance for judging existance of a user
        new_score = ContestScore(user=user, score=score)
        new_score.save()


def clear_contest_score(user):
    try:
        contest_score = ContestScore.objects.get(user=user)
        if ContestScore.objects.all().filter(pk=contest_score.pk).exists():
            contest_score.score = 0
            contest_score.save()
    except ObjectDoesNotExist:
        # A good performance for judging existance of a user
        new_score = ContestScore(user=user, score=0)
        new_score.save()


def judge_time_up(user, room):
    roomid = room.id
    userid = user.id
    cachekey = 'room' + str(roomid)
    currentid = cache.get(cachekey)
    if currentid is None:
        cache.set(cachekey, str(user.id) )
    else:
        currentval = cache.get(cachekey)
        if (currentval != str(userid)):
            cache.delete(cachekey)
            return True
        else:
            return False
    return False


def judge_contest_status(user, room):
    members = room.room_profile_set.all()
    first = members.first().user
    last = members.last().user
    origin_level = user.profile.level
    # Room has only one person
    # Will not count into database
    if first == last:
        if user == first:
            return "-"
        else:
            return "-"
    # Room has two persons
    else:
        first_score = ContestScore.objects.get(user=first).score
        last_score = ContestScore.objects.get(user=last).score
        if (first == user):
            if first_score > last_score:
                user.profile.level = origin_level + 1
                user.profile.save()
                return "Win"
            elif first_score == last_score:
                return "Tie"
            else:
                if origin_level != 0:
                    user.profile.level = origin_level - 1
                    user.profile.save()
                return "Lose"

        elif (last == user):
            if first_score > last_score:
                if origin_level != 0:
                    user.profile.level = origin_level - 1
                    user.profile.save()
                return "Lose"
            elif first_score == last_score:
                return "Tie"
            else:
                user.profile.level = origin_level + 1
                user.profile.save()
                return "Win"

        else:
            return "Unknown user"

def get_score(user):
    contest_score = ContestScore.objects.get(user=user)
    return contest_score.score


def match_user(user):
    room = Rooms.objects.get(pk=1)
    room_profiles = room.room_profile_set.all().order_by('time').reverse()
    for p in room_profiles:
        if p.user.profile.grade == user.profile.grade:
            return p
    return None

def create_new_room(user1, user2):
    title = user1.username + "  vs  " + user2.username
    new_room = Rooms(title=title)
    new_room.save()
    return new_room
