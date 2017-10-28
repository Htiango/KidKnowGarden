from django.conf.urls import url
from kidKnowGarden.views import *
from django.contrib.auth.views import LoginView

urlpatterns = [
    url(r'^$', welcome, name='welcome-page'),
    url(r'^register', register, name='register'),
    url(r'^login', login_page, name='login-page'),
    url(r'^accounts/login', LoginView.as_view(template_name='pages/logIn.html'), name='auto-login'),
    url(r'^activate/(?P<username>[^/]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
    url(r'^profile/setting', set_profile, name='set-profile'),
    url(r'^home', home, name='home'),
    url(r'^avatar/(?P<username>\w+)$', get_avatar, name='get-avatar'),
    url(r'^user/(?P<username>.+)/$', user_page_view, name='user-link'),
    url(r'^logout', logout_view, name='logout'),
]