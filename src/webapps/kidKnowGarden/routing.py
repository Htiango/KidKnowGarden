from channels.routing import route, route_class
from kidKnowGarden.consumers import *
from channels import include

# There's no path matching on these routes; we just rely on the matching
# from the top-level routing. We could path match here if we wanted.
websocket_routing = [
    # Called when WebSockets connect
    route("websocket.connect", ws_connect),

    # Called when WebSockets get sent a data frame
    route("websocket.receive", ws_receive),

    # Called when WebSockets disconnect
    route("websocket.disconnect", ws_disconnect),
]

# You can have as many lists here as you like, and choose any name.
# Just refer to the individual names in the include() function.
custom_routing = [
    # Handling different chat commands (websocket.receive is decoded and put
    # onto this channel) - routed on the "command" attribute of the decoded
    # message.
    route("chat.receive", chat_join, command="^join$"),
    route("chat.receive", chat_leave, command="^leave$"),
    route("chat.receive", answer, command="^answer$"),
    route("chat.receive", start_timing, command="^start$"),
    route("chat.receive", chat_send, command="^send$"),
    route("chat.receive", request_score, command="^score$"),

]