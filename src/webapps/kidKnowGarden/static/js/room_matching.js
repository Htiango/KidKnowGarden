$(function () {
    // Initialize action of Web Socket
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + ":8000" + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    var socket = new ReconnectingWebSocket(ws_path);

    // The boolean value will set to true and cannot be modified once the contest has started
    var has_contest_started = false;

    //Global variables initializations
    var roomId = $("#room").attr("room-id");

    var title = $("#title");
    var start_btn = $("#start");
    var messages = $("#messages");
    var status = $("#status");
    var username = $("#username");
    var host = "http://" + window.location.hostname + ":" + window.location.port;


    // Helpful debugging
    socket.onopen = function () {
        console.log("Connected to chat socket");
        // Join room
        socket.send(JSON.stringify({
            "command": "join",
            "room": roomId
        }));
    };
    socket.onclose = function () {
        console.log("Disconnected from chat socket");
        // Leave room
    };

    socket.onmessage = function (message) {
        // Decode the JSON
        console.log("Got websocket message " + message.data);
        var data = JSON.parse(message.data);
        // Handle errors
        if (data.error) {
            alert(data.error);
            return;
        }
        // Handle joining
        if (data.join) {
            console.log("Joining room " + data.join);
            start_btn.off().on("click", function () {
                socket.send(JSON.stringify({
                    "command": "start",
                    "room": data.join
                }));
            });
            var num = data.members;
        // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
        } else if (data.matched) {
            window.location.replace(host + data.matched);
        }
        else if (data.message) {
            // TODO: ADDING VANISHING POP UP COMPONENTS
            if (data.message === "USER ENTER"){
                //var ok_msg = "";
                ok_msg = "<div class='message alert alert-primary single-message-container'>" +
                    data.username + " is now finding opponent! " +
                    "</div>";
                messages.append(ok_msg);
                messages.scrollTop(messages.prop("scrollHeight"));
            }
            else if (data.message === "USER LEAVE"){
                //var ok_msg = "";
                ok_msg = "<div class='message alert alert-primary single-message-container'>" +
                    data.username + " is now leaving" +
                    "</div>";
                messages.append(ok_msg);
                messages.scrollTop(messages.prop("scrollHeight"));
            }
            else if (data.message === "MATCHED" && data.username === username.text()){
                window.location.replace(host + data.xmessage);
            }
        }
        else {
            console.log(data);
            console.log("Cannot handle message!");
        }
    };


    $( window ).on("unload", function(e) {
        socket.send(JSON.stringify({
            "command": "leave",  // determines which handler will be used (see chat/routing.py)
            "room": roomId
        }));
    });
});
