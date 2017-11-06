       $(function () {
            // Correctly decide between ws:// and wss://
            var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
            var ws_path = ws_scheme + '://' + window.location.host + "/chat/stream/";
            console.log("Connecting to " + ws_path);
            var socket = new ReconnectingWebSocket(ws_path);

            var disable_helper_function;
            var timeout;
            var intervalID;
            var currenttime = 0;

            // Helpful debugging
            socket.onopen = function () {
                console.log("Connected to chat socket");
            };
            socket.onclose = function () {
                console.log("Disconnected from chat socket");
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
                    $("#back-to-room-list").attr("hidden", false);
                    $("#all-room-list").attr("hidden", true);
                    console.log("Joining room " + data.join);
                    // language=DjangoTemplate
                    var roomdiv = $(
                        "<div id='timer' class='room-center timer-text'></div> " +
                        "<div class='room' id='room-" + data.join + "'>" +
                        "<div class='room-center'>" +
                        "<h2 id='title'>" + data.title + "</h2>" +
                        "<h5 id='status'></h5></div>" +
                        "<div class='messages' id='messages'></div>" +
                        "<div id='answer_group' class='display-contest-form' hidden></div><br>" +
                        "<div class='room-center'>" +
                        "<button id='start' class='btn btn-primary' hidden> START </button>" +
                        "</div>" +
                        "</div>"
                    );
                    $("#chats").append(roomdiv);

                    var start_button = $("#start");
                    start_button.on("click", function () {
                        socket.send(JSON.stringify({
                            "command": "start",
                            "room": data.join
                        }));

                    });

                    var num = data.members;
                    if (num === '2'){
                        $("#status").text("Ready to go! Hit start button to start contest.");
                        start_button.attr("hidden", false);
                    }
                    else{
                        $("#status").text("Wait for another people to join to start the contest.");
                        start_button.attr("hidden", true);
                    }

                // Handle leaving
                } else if (data.leave) {
                    console.log("Leaving room " + data.leave);
                    $("#room-" + data.leave).remove();
                }
                // TODO: EXTREMELY DANGEROUS BEHAVIOUR TO CORRECT!!!! SET TIME IN EXPLICITLY SET DIGIT!
                else if (data.message) {

                    disable_helper_function = function disable() {
                        var radios = $('input:radio[name=choice]');
                        radios.prop('disabled', true);
                        $("#submit-btn").prop('disabled', true);
                        socket.send(JSON.stringify({
                            "command": "score",
                            "room": data.room
                        }));
                    };

                    if (data.message === "Start timing" && data.xmessage === "Start timing") {
                        timeout = setTimeout(disable_helper_function, 15000);
                        $("button.answer").prop('disabled', false);
                        currenttime = 15;
                        $("#timer").html("<h2>" + currenttime + "</h2>");
                        intervalID = setInterval(function () {
                            currenttime = currenttime - 1;
                            if (currenttime === 0) {
                                this.clearInterval(intervalID);
                            }
                            $("#timer").html("<h2>" + currenttime + "</h2>");
                        }, 1000);
                    }

                    else if (data.message === "USER ENTER" || data.message === "USER LEAVE"){
                        var member_num = data.xmessage;
                        if (member_num === '2'){
                            $("#status").text("Ready to go! Hit start button to start contest.");
                            $("#start").attr("hidden", false);
                        }
                        else{
                            $("#status").text("Wait for another people to join to start the contest.");
                            $("#start").attr("hidden", true);
                        }
                    }

                    else if (data.xmessage === "Question") {
                        $("#back-to-room-list").attr("hidden", true);
                        $("#start").attr("hidden", true);
                        $("#messages").empty();
                        $("#status").empty();
                        var answer_group = $("#answer_group");
                        answer_group.empty();
                        answer_group.attr('hidden', false);
                        $("#submit-btn").attr('hidden', false);
                        var question_string = data.message;
                        var arr = question_string.split("#");
                        var title = $("#title");
                        title.text(arr[4]);
                        var choicediv = $(
                            "<input type='hidden' id='record_id' value=\"" + arr[5] + "\" hidden>" +
                            "<div class='choice-row form-check-label'>" +
                            "<input type='radio' name='choice' id='choice1' class='form-check-input' value=\"" + arr[0] + "\">" + arr[0] + "<br>" +
                            "</div>" +
                            "<div class='choice-row form-check-label'>" +
                            "<input type='radio' name='choice' id='choice2' class='form-check-input' value=\"" + arr[1] + "\">" + arr[1] + "<br>" +
                            "</div>" +
                            "<div class='choice-row form-check-label'>" +
                            "<input type='radio' name='choice' id='choice3' class='form-check-input' value=\"" + arr[2] + "\">" + arr[2] + "<br>" +
                            "</div>" +
                            "<div class='choice-row form-check-label'>" +
                            "<input type='radio' name='choice' id='choice4' class='form-check-input' value=\"" + arr[3] + "\">" + arr[3] + "<br>" +
                            "</div>" +
                            "<div class='btn-submit-row'>" +
                            "<button id='submit-btn' class='btn btn-primary'> submit</button>" +
                            "</div>"
                        );
                        answer_group.append(choicediv);
                        var submit_button = $("#submit-btn");
                        submit_button.prop("disabled", false);
                        submit_button.on("click", function () {
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
                            console.log("clicked" + data.room + index);
                            if (index >= 0) {
                                var id = $("#record_id").attr("value");
                                console.log(id);
                                socket.send(JSON.stringify({
                                    "command": "answer",
                                    "room": data.room,
                                    "record_id": id,
                                    "answer": index,
                                    "current_time": currenttime
                                }));
                            }
                        });
                    }

                    else {
                        var msgdiv = $("#room-" + data.room + " .messages");
                        //var ok_msg = "";
                        ok_msg = "<div class='message alert alert-primary single-message-container'>" +
                            data.username + " : "  + data.message +
                            "</div>";
                        msgdiv.append(ok_msg);
                        msgdiv.scrollTop(msgdiv.prop("scrollHeight"));
                    }

                } else if (data.answer) {
                    console.log(data);
                    var radios = $('input:radio[name=choice]');
                    radios.prop('disabled', true);
                    $("#submit-btn").prop("disabled", true);
                } else if (data.score) {
                    var next_button = $("#start");
                    next_button.attr("hidden", false);
                    next_button.text("Next");
                    $("#status").text(data.username + " : " + data.isWin + " ( Total Score: " + data.score + " )")
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

            // Room join/leave
            $("#back-to-room-list").click(function () {
                $("#back-to-room-list").attr("hidden", true);
                $("#all-room-list").attr("hidden", false);
                $("#chats").empty();

                clearInterval(intervalID);
                // Leave room
                $(this).attr("room-id", "");
                socket.send(JSON.stringify({
                    "command": "leave",  // determines which handler will be used (see chat/routing.py)
                    "room": roomId
                }));
            });

            $("button.room-link").click(function () {
                roomId = $(this).attr("data-room-id");
                // Join room
                console.log("Clicked!");
                $("#back-to-room-list").attr("room-id", roomId);
                //$(this).addClass("joined");
                socket.send(JSON.stringify({
                    "command": "join",
                    "room": roomId
                }));
            });


        });