from channels.auth import channel_session_user_from_http, channel_session_user
import json
from channels import Channel

from .utils import *
from .models import Rooms

from django.core.urlresolvers import reverse

@channel_session_user_from_http
def ws_connect(message):
    """
    Establish connection to websocket
    :param: message - channels header
    """
    message.reply_channel.send({"accept": True})
    message.channel_session['rooms'] = []


@channel_session_user
def ws_disconnect(message):
    """
    Disconnect from websocket
    :param: message - channels header
    """

    # Unsubscribe from any connected rooms
    for room_id in Rooms.objects.values_list('id', flat=True):
        try:
            room = Rooms.objects.get(pk=room_id)
            members = room.room_profile_set.count()
            if members > 0:
                if room.room_profile_set.all().filter(user=message.user).exists():
                    print("Triggers disconnect user leave")
                    room.send_message("USER LEAVE", message.user, members - 1)
                    room_profile = Room_Profile.objects.get(user=message.user)
                    room_profile.inroom = None
                    room_profile.save()
            # Removes us from the room's send group. If this doesn't get run,
            # we'll get removed once our first reply message expires.
            room.websocket_group.discard(message.reply_channel)
        except Rooms.DoesNotExist:
            pass


# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# This doesn't need @channel_session_user as the next consumer will have that,
# and we preserve message.reply_channel (which that's based on)
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    Channel("chat.receive").send(payload)


# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
def chat_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    """
    Dealing with chatroom joining semantics
    :param: message - channels header
    """
    try:
        room = get_room_or_error(message["room"], message.user)
    except:
        message.reply_channel.send({
            "text": json.dumps({
                "error": "You have no access to the room!",
            }),
        })
        return

    if is_in_another_room(message.user):
        message.reply_channel.send({
            "text": json.dumps({
                "error": "You are already in one contest!",
            }),
        })
    else:
        if room.id == 1:
            result = match_user(message.user)
            if result is None:
                room_profile = Room_Profile.objects.get(user=message.user)
                room.room_profile_set.add(room_profile)
                room.save()
                # Send a "enter message" to the room if available
                room.send_message("USER ENTER", message.user, None)
                room.websocket_group.add(message.reply_channel)
                message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
                message.reply_channel.send({
                    "text": json.dumps({
                        "join": str(room.id),
                        "title": room.title,
                    }),
                })
            else:
                # Generate a new room for the users
                new_room = create_new_room(message.user, result.user)
                new_url = reverse('room', kwargs={'id': new_room.id})
                room.send_message("MATCHED", result.user, new_url)
                message.reply_channel.send({
                    "text": json.dumps({
                        "matched": new_url,
                        "title": new_room.title,
                    }),
                })
        else:
            # Add one for this room
            clear_contest_score(message.user)
            members = room.room_profile_set.count()
            if members >= 2:
                message.reply_channel.send({
                    "text": json.dumps({
                        "error": "The contest has reach a member limit!",
                    }),
                })
            else:
                if room.room_profile_set.all().filter(user=message.user).exists():
                    message.reply_channel.send({
                        "text": json.dumps({
                            "error": "You are already in this contest!",
                        }),
                    })
                else:
                    room_profile = Room_Profile.objects.get(user=message.user)
                    room.room_profile_set.add(room_profile)
                    room.save()
                    # Send a "enter message" to the room if available
                    room.send_message("USER ENTER", message.user, str(members+1))

                    # OK, add them in. The websocket_group is what we'll send messages
                    # to so that everyone in the chat room gets them.
                    room.websocket_group.add(message.reply_channel)
                    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
                    # Send a message back that will prompt them to open the room
                    # Done server-side so that we could, for example, make people
                    # join rooms automatically.
                    message.reply_channel.send({
                        "text": json.dumps({
                            "join": str(room.id),
                            "title": room.title,
                            "members": str(members+1)
                        }),
                    })

@channel_session_user
def chat_leave(message):
    """
    Dealing with chatroom leaving semantics
    :param: message - channels header
    """
    # Reverse of join - remove them from everything.
    room = get_room_or_error(message["room"], message.user)
    members = room.room_profile_set.count()
    if members < 0:
        raise ClientError("ROOM_ACCESS_DENIED")
    else:
        if room.room_profile_set.all().filter(user=message.user).exists():
            room_profile = Room_Profile.objects.get(user=message.user)
            room_profile.inroom = None
            room_profile.save()

        # Send a "leave message" to the room if available
        room.send_message("USER LEAVE", message.user, members-1)

        room.websocket_group.discard(message.reply_channel)
        message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))
        # Send a message back that will prompt them to close the room
        message.reply_channel.send({
            "text": json.dumps({
                "leave": str(room.id),
            }),
        })
        if room.id != 1:
            room.delete()


@channel_session_user
def chat_send(message):
    """
    Generic message sending function for websocket room
    :param: message - channels header
    """
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    room.send_message(message["message"], message.user, None)


@channel_session_user
def answer(message):
    """
    Judge if the question is correct and save scores to the database
    :param: message - channels header
    """
    try:
        if int(message['room']) not in message.channel_session['rooms']:
            raise ClientError("ROOM_ACCESS_DENIED")
        room = get_room_or_error(message["room"], message.user)
        answer = message["answer"]
        record_id = message["record_id"]
        status = judge_question_correctness(int(record_id), int(answer))

        if status:
            answer = "Got the right answer!"
            score = message["current_time"]
            save_contest_score(score, message.user)
        else:
            answer = "Made a wrong guess!"
            save_contest_score(0, message.user)

        time_up = judge_time_up(message.user, room)
        # Send message to all members in the room
        room.send_message(answer, message.user, str(time_up))
        # Return a message only to the user who make a message request
        message.reply_channel.send({
            "text": json.dumps({
                "answer": answer,
                "correctness": status,
            }),
        })
    except:
        message.reply_channel.send({
            "text": json.dumps({
                "error": "You have no access to the room!",
            }),
        })



@channel_session_user
def start_timing(message):
    """
    Start another random question and pass it through websocket
    :param: message - channels header
    """
    try:
        if int(message['room']) not in message.channel_session['rooms']:
            raise ClientError("ROOM_ACCESS_DENIED")
        room = get_room_or_error(message["room"], message.user)
        if start_confirm(message.user, room):
            question_string = get_random_question(room)
            if question_string != "Contest End":
                room.send_message(question_string, message.user, "Question")
                room.send_message("Start timing", message.user, "Start timing")
            else:
                room.send_message("Contest End", message.user, "Contest End")
        else:
            room.send_message("Waiting for confirm", message.user, "Waiting for confirm")
    except:
        message.reply_channel.send({
            "text": json.dumps({
                "error": "You are no longer inside the contest room!",
            }),
        })


@channel_session_user
def request_score(message):
    """
    Users use this function to request score
    :param: message - channels header
    """
    # Return a message only to the user who make a message request
    # Three status of win/loss: Win, Lose or Tie
    message.reply_channel.send({
        "text": json.dumps({
            "score": str(get_score(message.user)),
            "username": message.user.username
        }),
    })


@channel_session_user
def request_result(message):
    """
    Users use this function to judge final result and save the result to database
    :param: message - channels header
    """
    try:
        if int(message['room']) not in message.channel_session['rooms']:
            raise ClientError("ROOM_ACCESS_DENIED")
        room = get_room_or_error(message["room"], message.user)

        # Return a message only to the user who make a message request
        # Three status of win/loss: Win, Lose or Tie
        message.reply_channel.send({
            "text": json.dumps({
                "result": str(get_score(message.user)),
                "isWin": judge_contest_status(message.user, room),
                "username": message.user.username
            }),
        })
    except:
        message.reply_channel.send({
            "text": json.dumps({
                "error": "You are no longer inside the contest room!",
            }),
        })
