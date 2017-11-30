$(function () {
    // Initialize action of Web Socket
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
    console.log("Connecting to " + ws_path);
    var socket = new ReconnectingWebSocket(ws_path);

    // The boolean value will set to true and cannot be modified once the contest has started
    var has_contest_started = false;

    //Global variables initializations
    var disable_helper_function;
    var timeout;
    var intervalID;
    var currenttime = 0;
    var timeout_s = 15;
    var roomId = $("#room").attr("room-id");

    var title = $("#title");
    var start_btn = $("#start");
    var messages_my = $("#messages1");
    var messages_opp = $("#messages2");
    var user_name = $.trim($("#user-name").text());
    var opponent_name = $.trim($("#opponent-name").text());

    var status = $("#status");
    var submit_btn = $("#submit-btn");
    var answer_group = $("#answer_group");
    var choice1 = $("#choice1");
    var choice2 = $("#choice2");
    var choice3 = $("#choice3");
    var choice4 = $("#choice4");
    var radios = $('input:radio[name=choice]');

    function request_score(){
        socket.send(JSON.stringify({
            "command": "score",
            "room": roomId
        }));
    }

    function request_result(){
        socket.send(JSON.stringify({
            "command": "result",
            "room": roomId
        }));
    }

    function initial_status(){
        // messages.empty();
        messages_my.empty();
        messages_opp.empty();

        status.empty();
        start_btn.prop("hidden", true);
        answer_group.prop('hidden', true);
        submit_btn.prop('hidden', true);
        clearInterval(intervalID);
        clearTimeout(timeout);
        $("#timer").empty();
    }

    function disable_answers(){
        radios.prop('disabled', true);
        submit_btn.prop("disabled", true);
    }

    function start_again(){
        start_btn.prop("hidden", false);
        start_btn.text("Next");
    }

    function contest_end(){
        title.text("Contest ends.");
        // messages.empty();
        messages_my.empty();
        messages_opp.empty();

        status.empty();
        start_btn.prop("hidden", true);
        answer_group.prop('hidden', true);
        submit_btn.prop('hidden', true);
        clearInterval(intervalID);
        clearTimeout(timeout);
        $("#timer").empty();
    }

    function contest_stop(){
        clearInterval(intervalID);
        clearTimeout(timeout);
        $("#timer").html("<h2> Finished! </h2>");
        disable_answers();
        request_score();
        start_again();
    }

    function judge_user_num(member_num, user_leave){
        if (member_num === '2'){
            if (!has_contest_started){
                status.text("Ready to go! Hit start button to start contest.");
                start_btn.prop("hidden", false);
            }
        }
        else{
            if (!has_contest_started){
                initial_status();
                status.text("Wait for another people to join to start the contest.");
                start_btn.prop("hidden", true);
                if (user_leave){
                    contest_end();
                    status.text("Your opponent has left the contest");
                }
            }
            else{
                contest_end();
                request_score();
            }

        }
    }

    function on_start_question(arr){
        radios.prop("checked", false);
        radios.prop('disabled', false);
        submit_btn.prop("disabled", false);
        // messages.empty();
        messages_my.empty();
        messages_opp.empty();

        status.empty();
        start_btn.prop("hidden", true);

        answer_group.prop('hidden', false);
        submit_btn.prop('hidden', false);
        title.text(arr[4]);
        $("#record_id").prop("value", arr[5]);
        choice1.prop("value", arr[0]);
        choice2.prop("value", arr[1]);
        choice3.prop("value", arr[2]);
        choice4.prop("value", arr[3]);
        choice1.next().text(arr[0]);
        choice2.next().text(arr[1]);
        choice3.next().text(arr[2]);
        choice4.next().text(arr[3]);
    }

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
            judge_user_num(num);

        // Handle leaving
        } else if (data.leave) {
            console.log("Leaving room " + data.leave);
        }

        else if (data.message) {
            disable_helper_function = function disable() {
                disable_answers();
                request_score();
                start_again();
            };

            if (data.message === "Start timing" && data.xmessage === "Start timing") {
                timeout = setTimeout(disable_helper_function, timeout_s * 1000);
                currenttime = timeout_s;
                $("#timer").html("<h2>" + currenttime + "</h2>");
                intervalID = setInterval(function () {
                    currenttime = currenttime - 1;
                    $("#timer").html("<h2>" + currenttime + "</h2>");
                    if (currenttime === 0) {
                        this.clearInterval(intervalID);
                        $("#timer").html("<h2> Time up! </h2>");

                    }
                }, 1000);
            }

            else if (data.message === "Contest End" && data.xmessage === "Contest End") {
                contest_end();
                request_result();
            }

            else if (data.message === "Waiting for confirm" && data.xmessage === "Waiting for confirm") {
                status.text("Wait for another people proceed.");
            }

            else if (data.message === "USER ENTER" || data.message === "USER LEAVE"){
                var member_num = data.xmessage;
                var user_leave = false;
                if (data.message === "USER LEAVE") {
                    user_leave = true;
                }
                judge_user_num(member_num, user_leave);
            }

            else if (data.xmessage === "Question") {
                var question_string = data.message;
                var arr = question_string.split("#");
                has_contest_started = true;
                on_start_question(arr);

                submit_btn.off().on("click", function () {
                    var index = -1;
                    if ($("#choice1").is(":checked")) {
                        index = 0;
                    }
                    else if ($("#choice2").is(":checked")) {
                        index = 1;
                    }
                    else if ($("#choice3").is(":checked")) {
                        index = 2;
                    }
                    else if ($("#choice4").is(":checked")) {
                        index = 3;
                    }
                    console.log("clicked" + roomId + index);
                    if (index >= 0) {
                        var id = $("#record_id").prop("value");
                        console.log(id);
                        socket.send(JSON.stringify({
                            "command": "answer",
                            "room": roomId,
                            "record_id": id,
                            "answer": index,
                            "current_time": currenttime
                        }));
                    }
                });
            }
            else {
                // This branch only deals with user's correctness message.
                // If expansion of function is needed, changes shall apply to this branch
                ok_msg = "<div class='message alert alert-primary single-message-container'>" +
                    data.username + " : "  + data.message +
                    "</div>";
                console.log(data.username);
                console.log(typeof(data.username));
                console.log(data.username.length);
                console.log(user_name);
                console.log(typeof(user_name));
                console.log(user_name.length);
                if (data.username === user_name){
                    messages_my.append(ok_msg);
                }
                else{
                    messages_opp.append(ok_msg);
                }
                // messages.append(ok_msg);
                // messages.scrollTop(messages.prop("scrollHeight"));
                if (data.xmessage === 'True' || data.xmessage === 'true'){
                    contest_stop();
                }
            }
        } else if (data.answer) {
            disable_answers();
        } else if (data.score) {
            status.text(data.username + " : " + " Total Score: " + data.score)
        } else if (data.result) {
            status.text(data.username + " : " + data.isWin + " ( Total Score: " + data.result + " )")
        }
        else {
            console.log(data);
            console.log("Cannot handle message!");
        }
    };

    // Says if we joined a room or not by if there's a div for it
    function inRoom(roomId) {
        return $("#room-" + roomId).length > 0;
    }

    window.onbeforeunload = function() {
       return "Are you sure you want to navigate away?";
    };

    $( window ).on("unload", function(e) {
        socket.send(JSON.stringify({
            "command": "leave",  // determines which handler will be used (see chat/routing.py)
            "room": roomId
        }));
    });
});