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

});


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
}


function renderBoardCell(id) {
    var val = "";
    var maxlength =" maxlength='1' ";
    return "<div class='sudoku-board-cell'>" +
        //want to use type=number, but then have to prevent chrome scrolling and up down key behaviors..
        "<input type='text' novalidate id='input-" + id + "' value='" + val + "'" + maxlength + ">" +
        "</div>";
};