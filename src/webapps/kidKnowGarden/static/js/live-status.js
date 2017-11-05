
$( document ).ready(function() {
      var socket = new WebSocket('ws://' + window.location.host + '/users/');
      //username = $("#navbarDropdownMenuLink").html().trim();
      //var user_socket = new WebSocket('ws://' + window.location.host + '/user_status/' + username + '/');

      socket.onopen = function open() {
          console.log('WebSockets connection created.');
      };

      user_socket.onopen = function open() {
          console.log('User connection created.');
      };

      socket.onmessage = function message(event) {
          var data = JSON.parse(event.data);
          // NOTE: We escape JavaScript to prevent XSS attacks.
          var username = encodeURI(data['username']);
          var user = $('li').filter(function () {
              return $(this).data('username') === username;
          });

          if (data['is_logged_in']) {
              user.html(username + ': Online');
              $("#invite-" + username).show();
          }
          else {
              user.html(username + ': Offline' );
              $("#invite-" + username).hide();
          }
      };

      if (socket.readyState === WebSocket.OPEN) {
          socket.onopen();
      }

      // user_socket.onmessage = function message(event) {
      //     var data = JSON.parse(event.data);
      //     console.log(data);
      // };

      // if (user_socket.readyState === WebSocket.OPEN) {
      //     user_socket.onopen();
      // }
});
