from django.shortcuts import render
from kidKnowGarden.forms import *
from kidKnowGarden.models import *
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.core.mail import send_mail


def welcome(request):
    return render(request, 'pages/welcome.html', {})


def register(request):
    context = {}
    form = RegisterForm()
    context['form'] = form

    if request.method == 'GET':
        return render(request, 'pages/register.html', context)

    form = RegisterForm(request.POST)
    if not form.is_valid():
        return render(request, 'pages/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        password=form.cleaned_data['password1'])
    new_user.is_active = False
    new_user.save()

    token = default_token_generator.make_token(new_user)

    email_body = """
        Welcome to the grumblr. Please click the link below to verify your email address and complete the registration of your account:

        http://%s%s
    """ % (request.get_host(), reverse('activate', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="register@grumblr.com",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']

    return render(request, 'pages/notification.html', context)