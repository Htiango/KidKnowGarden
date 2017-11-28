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

    var record_id = $("#record_id").attr("value");
    var question_id = $("#question_id").attr("value");
    $("#record_id").remove();
    $("#question_id").remove();
    add_submit_listener(record_id, question_id);

});


function add_submit_listener(record_id, question_id) {
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
            console.log(record_id);
            $.post("/kidKnowGarden/submit-answer", {"record_id": record_id, "question_id": question_id, "index": index}).done(show_result);
        }
    })
}

function show_result(data){
    console.log(data);

    var result_left = $("#result-left");
    var result_right = $('#result-right');
    var status = data["status"];
    result_left.empty();
    result_right.empty();
    if (status == "True"){
        result_left.append($("<span class='mbr-iconfont mbri-smile-face question-feedback-icons' style='color: green;' media-simple='true'></span>"));
        result_left.append($("<br><br><span class='align-center question-success-text'>Correct!</span>"));
        result_right.append($("<span class='mbr-iconfont mbri-smile-face question-feedback-icons' style='color: green;' media-simple='true'></span>"));
        result_right.append($("<br><br><span class='align-center question-success-text'>Correct!</span>"));
    }
    else{
        result_left.append($("<span class='mbr-iconfont mbri-sad-face question-feedback-icons' style='color: red;' media-simple='true'></span>"));
        result_right.append($("<span class='mbr-iconfont mbri-sad-face question-feedback-icons' style='color: red;' media-simple='true'></span>"));
        result_left.append($("<br><br><span class='align-center question-wrong-text'>Sorry, wrong answer.<br>" +
            "Correct answer is: " + data["answer"] + "</span>"));
        result_right.append($("<br><br><span class='align-center question-wrong-text'>Sorry, wrong answer.<br>" +
            "Correct answer is: " + data["answer"] + "</span>"));
    }
}