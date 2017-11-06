/**
 * Created by hty on 05/11/2017.
 */

$(document).ready(function () {
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    console.log("hello");

    add_submit_listener();

});


function add_submit_listener() {
    var submit_btn = $("#submit-btn");
    submit_btn.click(function (event) {
        event.preventDefault();
        var index = -1;
        if ($("#choice1").is(":checked")){
            index = 0;
        }
        else if ($("#choice2").is(":checked")){
            index = 1;
        }
        else if ($("#choice3").is(":checked")){
            index = 2;
        }
        else if ($("#choice4").is(":checked")){
            index = 3;
        }
        console.log(index);
        if (index >= 0){
            var record_id = $("#record_id").attr("value");
            var question_id = $("#question_id").attr("value");
            console.log(record_id);
            $.post("/kidKnowGarden/submit-answer", {"record_id": record_id, "question_id": question_id, "index": index}).done(show_result);
        }
    })
}

function show_result(data){
    console.log(data);

    var result = $("#result");
    var status = data["status"];
    result.empty();
    if (status == "True"){
        result.append($("<div class='alert alert-success alert-text' role='alert'> Correct!</div>"));
    }
    else{
        result.append($("<div class='alert alert-danger alert-text' role='alert'> Wrong!</div>"));
        result.append($("<div class='alert alert-primary alert-text' id='correct_answer' role='alert'> </div>"));
        $("#correct_answer").append("ANSWER: " + data["answer"]);
    }
}