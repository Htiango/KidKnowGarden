from functools import wraps

from .exception import ClientError
from .models import Rooms, Profile



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