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

});


function hint_listener() {
    var hint_btn = $('#hint-btn');
    hint_btn.click(function (event){
        getOneHint();
    })
}

function replay_listener() {
    var replay_btn = $("#replay-btn");
    replay_btn.click(function (event){
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

function getNewSudoku(){
    $.get("/kidKnowGarden/sudoku-game/generate-sudoku").done(display_sudoku);
}

function renderBoardCell(id) {
    var val = "";
    var maxlength =" maxlength='1' ";
    return "<div class='sudoku-board-cell'>" +
        //want to use type=number, but then have to prevent chrome scrolling and up down key behaviors..
        "<input type='text' novalidate id='input-" + id + "' value='" + val + "'" + maxlength + ">" +
        "</div>";
};


function display_sudoku(data){
    var sudoku_list = $.parseJSON(data["sudoku"]);
    for (var i=0; i < sudoku_list.length; i++){
        var input = $('#input-' + i);
        if (sudoku_list[i] != 0){
            input.val(sudoku_list[i]);
            input.attr('readonly', true);
        }
        else{
            input.val("");
        }
    }
}

function getCurrentSudoku() {
    var sudoku = [];
    for (var i=0; i<81; i++){
        var value = $('#input-'+i).val();
        if (value != ''){
            sudoku.push(value);
        }
        else{
            sudoku.push("0");
        }
    }
    // console.log(sudoku);
    return sudoku
}


function getOneHint(){
    var sudoku = getCurrentSudoku();
    console.log(sudoku);
    var sudoku_json = sudoku.join()
    $.get("/kidKnowGarden/sudoku-game/give-one-hint", {'sudoku': sudoku_json}).done(display_one_hint);
}

function display_one_hint(data) {
    console.log(data);
    var index = data["index"];
    var answer = data["answer"];
    var input = $('#input-' + index);
    input.val(answer);
    input.focus();
}