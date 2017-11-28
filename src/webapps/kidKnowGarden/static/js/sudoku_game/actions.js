/**
 * Created by hty on 16/11/2017.
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
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    console.log("hello");

    generateBoard();

    replay_listener();
    hint_listener();
    answer_listener();
    submit_listener();

});


function submit_listener() {
    var check_btn = $('#check-btn');
    check_btn.click(function (event) {
        checkAnswer();
    })
}


function answer_listener() {
    var answer_btn = $('#answer-btn');
    answer_btn.click(function (event) {
        getAnswer();
    })
}

function hint_listener() {
    var hint_btn = $('#hint-btn');
    hint_btn.click(function (event) {
        getOneHint();
    })
}

function replay_listener() {
    var replay_btn = $("#replay-btn");
    replay_btn.click(function (event) {
        getNewSudoku();
    })
}

function generateBoard() {
    var board = $("#sudoku_board");
    var htmlString = "";
    for (var i = 0; i < 9 * 9; i++) {
        htmlString += renderBoardCell(i);

        if ((i + 1) % 9 === 0) {
            htmlString += "<br>";
        }
    }
    board.append(htmlString);
    getNewSudoku();
}

function getNewSudoku() {
    var level = 1;
    if ($("#radio2").is(":checked")){
        level = 2;
    }
    if ($("#radio3").is(":checked")){
        level = 3;
    }
    $.get("/kidKnowGarden/sudoku-game/generate-sudoku", {"level": level})
        .done(display_sudoku)
        .fail(function () {
            error_info("Internal Error Happens")
        });
}

function renderBoardCell(id) {
    var val = "";
    var maxlength = " maxlength='1' ";
    return "<div class='sudoku-board-cell'>" +
        //want to use type=number, but then have to prevent chrome scrolling and up down key behaviors..
        "<input type='text' novalidate id='input-" + id + "' value='" + val + "'" + maxlength + ">" +
        "</div>";
};


function display_sudoku(data) {
    var sudoku_list = $.parseJSON(data["sudoku"]);
    for (var i = 0; i < sudoku_list.length; i++) {
        var input = $('#input-' + i);
        input.attr('readonly', false);
        input.removeClass("highlight-val");
        if (sudoku_list[i] != 0) {
            input.val(sudoku_list[i]);
            input.attr('readonly', true);
        }
        else {
            input.val("");
            input.addClass("highlight-val")
        }
    }
}

function getCurrentSudoku() {
    var sudoku = [];
    for (var i = 0; i < 81; i++) {
        var value = $('#input-' + i).val();
        if (value != '') {
            sudoku.push(value);
        }
        else {
            sudoku.push("0");
        }
    }
    // console.log(sudoku);
    return sudoku
}

function getOneHint() {
    var sudoku = getCurrentSudoku();
    console.log(sudoku);
    var sudoku_json = sudoku.join();
    $.get("/kidKnowGarden/sudoku-game/give-one-hint", {'sudoku': sudoku_json})
        .done(display_one_hint)
        .fail(function () {
            error_info("Internal Error Happens");
        });
}

function display_one_hint(data) {
    console.log(data);
    var index = data["index"];
    if (!index) {
        return
    }
    if (index == "-1") {
        error_info('You Input Wrong Answers Somewhere!');
        return;
    }
    if (index == "-2") {
        error_info('You Have Informal Input Somewhere!')
        return;
    }
    var answer = data["answer"];
    var input = $('#input-' + index);
    input.val(answer);
    input.attr('readonly', true);
    input.addClass("board-cell-hint")
    setTimeout(function () {
        input.removeClass("board-cell-hint");
    }, 800);
}

function getAnswer() {
    $('.highlight-val').each(function (i, obj) {
        $(this).val("")
    });
    var sudoku = getCurrentSudoku();
    var sudoku_json = sudoku.join();

    $.get("/kidKnowGarden/sudoku-game/get-solution", {'sudoku': sudoku_json})
        .done(display_sudoku)
        .fail(function () {
            error_info("Internal Error Happens");
        });
}


function checkAnswer() {
    var sudoku = getCurrentSudoku();
    var sudoku_json = sudoku.join();
    $.get("/kidKnowGarden/sudoku-game/check-answer", {'sudoku': sudoku_json})
        .done(display_check)
        .fail(function () {
            error_info("Internal Error Happens")
        });
}


function display_check(data) {
    // console.log(typeof(data))
    if (data == 1) {
        success_info('Well Done!');
    }
    else if (data == 0) {
        warning_info('Please Complete Game Before Check!');
        // alert("Please complete board!");
    }
    else {
        error_info('You Input Wrong Answers Somewhere!');
    }

}


function success_info(content) {
    $.alert({
        title: 'SUCCESS',
        titleClass: 'alert-success-text',
        icon: 'mbri-smile-face alert-success-text',
        content: content,
        theme: 'bootstrap',
        type: 'green'
    });
}


function error_info(content) {
    $.alert({
        title: 'ERROR',
        titleClass: 'alert-fail-text',
        icon: 'mbri-sad-face alert-fail-text',
        content: content,
        theme: 'bootstrap',
        type: 'red'
    });
}

function warning_info(content) {
    $.alert({
        title: 'WARNING',
        titleClass: 'alert-warning-text',
        icon: 'mbri-sad-face alert-warning-text',
        content: content,
        theme: 'bootstrap',
        type: 'orange'
    });
}