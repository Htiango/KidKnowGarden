from channels.auth import channel_session_user_from_http
from channels.auth import channel_session_user_from_http, channel_session_user
import json
from channels import Channel

from .utils import *
from .models import Rooms

@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({"accept": True})
    message.channel_session['rooms'] = []


@channel_session_user
def ws_disconnect(message):
    # Unsubscribe from any connected rooms
    #for room_id in message.channel_session.get("rooms", set()):
    for room_id in Rooms.objects.values_list('id', flat=True):
        try:
            room = Rooms.objects.get(pk=room_id)
            members = room.members.count()
            if members > 0:
                # A bad performance for judging user existence
                if message.user in room.members.all():
                    room.members.remove(message.user)
                    room.save()
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
#@catch_client_error
def chat_join(message):
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    room = get_room_or_error(message["room"], message.user)

    ## Add one for this room
    clear_contest_score(message.user)
    members = room.members.count()
    if members >= 2:
        raise ClientError("ROOM_ACCESS_DENIED")
    else:
        if message.user in room.members.all():
            raise ClientError("ROOM_ACCESS_DENIED")
        else:
            room.members.add(message.user)
            room.save()
            # Send a "enter message" to the room if available
            #if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
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
#@catch_client_error
def chat_leave(message):
    # Reverse of join - remove them from everything.
    room = get_room_or_error(message["room"], message.user)

    members = room.members.count()
    if members < 0:
        raise ClientError("ROOM_ACCESS_DENIED")
    else:
        if message.user in room.members.all():
            room.members.remove(message.user)
            room.save()

        # Send a "leave message" to the room if available
        #if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message("USER LEAVE", message.user, None)

        room.websocket_group.discard(message.reply_channel)
        message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))
        # Send a message back that will prompt them to close the room
        message.reply_channel.send({
            "text": json.dumps({
                "leave": str(room.id),
            }),
        })


@channel_session_user
#@catch_client_error
def chat_send(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    room.send_message(message["message"], message.user, None)


@channel_session_user
#@catch_client_error
def answer(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)
    answer = message["answer"]
    record_id = message["record_id"]
    status = judge_question_correctness(int(record_id), int(answer))

    if status:
        answer = "Got the right answer!"
        score = message["current_time"]
        save_contest_score(score,message.user)
    else:
        answer = "Made a wrong guess!"
        save_contest_score(0, message.user)

    # Send message to all members in the room
    room.send_message(answer, message.user, "A new room status of scores")
    # Return a message only to the user who make a message request
    message.reply_channel.send({
        "text": json.dumps({
            "answer": answer,
            "correctness": status
        }),
    })


@channel_session_user
#@catch_client_error
def start_timing(message):
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    room = get_room_or_error(message["room"], message.user)

    question_string = get_random_question()
    #print(question_string)
    room.send_message(question_string, message.user, "Question")
    room.send_message("Start timing", message.user, "Start timing")


@channel_session_user
#@catch_client_error
def request_score(message):
    # if int(message['room']) not in message.channel_session['rooms']:
    #     raise ClientError("ROOM_ACCESS_DENIED")

    room = get_room_or_error(message["room"], message.user)

    print("This is score operation" + message['room'])
    # Return a message only to the user who make a message request
    # Three status of win/loss: Win, Lose or Tie
    message.reply_channel.send({
        "text": json.dumps({
            "score": str(get_score(message.user)),
            "isWin": judge_contest_status(message.user, room),
            "username": message.user.username
        }),
    })
