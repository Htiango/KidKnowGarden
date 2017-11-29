from django.conf.urls import url
from kidKnowGarden.views import *
from django.contrib.auth.views import LoginView


urlpatterns = [
    url(r'^$', welcome, name='welcome-page'),
    url(r'^register', register, name='register'),
    url(r'^login', login_page, name='login-page'),
    url(r'^accounts/login', LoginView.as_view(template_name='pages/login.html'), name='auto-login'),
    url(r'^activate/(?P<username>[^/]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
    url(r'^profile/setting$', set_profile, name='set-profile'),
    url(r'^edit-profile-page$', edit_profile_page, name='edit-profile-page'),
    url(r'^edit-profile$', edit_profile, name='edit-profile'),

    url(r'^profile-page$', profile_page, name='profile-page'),

    url(r'^learning-history$', question_history, name='learning-history'),

    url(r'^home', home, name='home'),
    url(r'^avatar/(?P<username>\w+)$', get_avatar, name='get-avatar'),
    url(r'^user/(?P<username>.+)/$', user_page_view, name='user-link'),
    url(r'^logout', logout_view, name='logout'),
    url(r'^room_list$', matching, name='room_list'),
    # url(r'^room/(?P<id>\d+)$', room, name='room'),
    url(r'^room/(?P<id>\d+)/(?P<user1>\w+)/(?P<user2>\w+)$', room, name='room'),
    #url(r'^user_list$', user_list, name='user_list'),
    #url(r'^user_invite/(?P<username>.+)/$', user_invite, name='user-invite'),

    url(r'^learn-page$', learn_page, name='learn_page'),
    url(r'^game-page$', game_page, name='game_page'),
    url(r'^question-of-grade$', question_grade, name='question_of_grade'),
    url(r'^question-list$', question_list, name='question_list'),
    url(r'^random-question$', random_question, name='random_question'),
    url(r'^question/(?P<question_id>.+)$', question_page, name='question-page'),
    url(r'^submit-answer$', check_answer, name="check_answer"),
    url(r'^memory-game$', memory_game, name="memory_game"),
    url(r'^sudoku-game$', sudoku_game, name="sudoku_game"),
    url(r'^sudoku-game/generate-sudoku$', generate_sudoku, name='generate_sudoku'),
    url(r'^sudoku-game/give-one-hint$', hint_sudoku, name='hint_sudoku'),
    url(r'^sudoku-game/get-solution$', get_sudoku_solution, name='get_solution'),
    url(r'^sudoku-game/check-answer$', check_sudoku_answer, name='check_answer')
]