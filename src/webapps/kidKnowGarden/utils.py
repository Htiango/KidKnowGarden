from functools import wraps

from .exception import ClientError
from .models import *

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


# Extend this function to return a set of string
# To generate questions and answers
def get_random_room():
    # Performance will be largely affected!!!
    room = Rooms.objects.order_by('?')
    r = room.first()
    return r.title

def get_random_question():
    question = Question.objects.order_by('?')
    q = question.first()
    # Shuffle choice and answers
    ls = [q.choice1, q.choice2, q.choice3, q.answer]
    random.shuffle(ls)
    index = ls.index(q.answer)
    new_record = CorrectAnswer(answer_index=index)
    new_record.save()
    question_string = ls[0] + "#" + ls[1] + "#" + ls[2] + "#" + ls[3] + "#" +  q.content + "#" + str(new_record.id)
    return question_string

def judge_question_correctness(record_id, answer_index):
    correct_answer = CorrectAnswer.objects.get(id=record_id)
    status = (correct_answer.answer_index == answer_index)
    return status

def save_contest_score(score, user):
    contest_score = ContestScore.objects.filter(user=user)
    if contest_score.count() > 0:
        prev_score = contest_score.score
        contest_score.score = prev_score + score
        contest_score.save()
    else:
        new_score = ContestScore(user=user, score=score)
        new_score.save()


def clear_contest_score(user):
    contest_score = ContestScore.objects.filter(user=user)
    if contest_score.count() > 0:
        contest_score.score = 0
        contest_score.save()