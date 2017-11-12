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
    url(r'^profile/setting', set_profile, name='set-profile'),
    url(r'^home', home, name='home'),
    url(r'^avatar/(?P<username>\w+)$', get_avatar, name='get-avatar'),
    url(r'^user/(?P<username>.+)/$', user_page_view, name='user-link'),
    url(r'^logout', logout_view, name='logout'),
    url(r'^room_list$', matching, name='room_list'),
    url(r'^room/(?P<id>\d+)$', room, name='room'),
    #url(r'^user_list$', user_list, name='user_list'),
    #url(r'^user_invite/(?P<username>.+)/$', user_invite, name='user-invite'),

    url(r'^learn-page$', learn_page, name='learn_page'),
    url(r'^question-list$', question_list, name='question_list'),
    url(r'^random-question$', random_question, name='random_question'),
    url(r'^question/(?P<question_id>.+)$', question_page, name='question-page'),
    url(r'^submit-answer$', check_answer, name="check_answer"),
    url(r'^memory-game$', memory_game, name="memory_game")
]