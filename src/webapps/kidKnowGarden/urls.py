from django.conf.urls import url
from kidKnowGarden.views import *

urlpatterns = [
    url(r'^$', welcome, name='welcome-page'),
    url(r'register', register, name='register'),
]