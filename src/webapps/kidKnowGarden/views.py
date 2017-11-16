from django.shortcuts import render, redirect, get_object_or_404
from kidKnowGarden.forms import *
from kidKnowGarden.models import *
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from mimetypes import guess_type
from django.contrib.auth import authenticate, login, logout
import random

from channels import Group

import json


# response a welcome page. If already login, then direct to the home page
def welcome(request):
    user = request.user
    if not user.is_anonymous:
        return redirect(home)
    return render(request, 'pages/welcome.html', {})


# If request method is get, then present the register page. Otherwise save the user, send activate email and direct to
# a notification page.
def register(request):
    user = request.user
    if not user.is_anonymous:
        return redirect(home)
    context = {}
    form = RegisterForm()
    context['form'] = form

    if request.method == 'GET':
        return render(request, 'pages/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

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


# login page
def login_page(request):
    user = request.user
    if not user.is_anonymous:
        return redirect(home)
    return render(request, 'pages/login.html', {})


def activate(request, username, token):
    user = User.objects.get(username=username)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect(set_profile)
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def set_profile(request):
    context = {}
    context['profile_form'] = ProfileForm()
    if request.method == 'GET':
        return render(request, 'pages/set_profile_new.html', context)

    profile_form = ProfileForm(request.POST, request.FILES)
    context['profile_form'] = profile_form

    if not profile_form.is_valid():
        return render(request, 'pages/set_profile_new.html', context)

    new_profile = Profile(user=request.user,
                          grade=profile_form.cleaned_data['grade']
                          )
    new_room_profile = Room_Profile(user=request.user)
    if profile_form.cleaned_data['avatar']:
        new_profile.avatar = profile_form.cleaned_data['avatar']
    if profile_form.cleaned_data['bio']:
        new_profile.bio = profile_form.cleaned_data['bio']
    new_profile.save()
    new_room_profile.save()
    return redirect(home)


@login_required
def home(request):
    context = {'user': request.user}
    #if not LoggedInUser.objects.filter(user=request.user):
    #    user_now = LoggedInUser(user=request.user)
    #    user_now.save()

    #users = User.objects.select_related('logged_in_user')
    #for user in users:
    #    user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
    #context['users'] = users
    return render(request, 'pages/home.html', context)


@login_required
def get_avatar(request, username):
    user = User.objects.filter(username=username)
    profile = get_object_or_404(Profile, user=user)

    if not profile.avatar:
        raise Http404

    content_type = guess_type(profile.avatar.name)
    return HttpResponse(profile.avatar, content_type=content_type)


@login_required
def user_page_view(request, username):
    try:
        user_select = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User does not exist!")
    user = request.user

    context = {'user': user, 'user_select': user_select}
    return render(request, 'pages/profile.html', context)


@login_required
def logout_view(request):
    #delete_user = LoggedInUser.objects.filter(user=request.user)
    #if delete_user:
    #    delete_user.delete()
    logout(request)
    return redirect(welcome)

@login_required
def matching(request):
    user = request.user
    return render(request, 'pages/room_matching.html', {"user": user})

@login_required
def room(request, id):
    if id == 1 or id == '1':
        raise Http404("Not found")
    else:
        room_object = get_object_or_404(Rooms, pk=id)
        return render(request, 'pages/room.html', {'room': room_object, "user": request.user})


# @login_required
# def user_list(request):
#     users = User.objects.select_related('logged_in_user')
#     for user in users:
#         user.status = 'Online' if hasattr(user, 'logged_in_user') else 'Offline'
#     return render(request, 'pages/user_list.html', {'users': users})

# @login_required
# def user_invite(request, username):
#     Group("user-" + username).send({
#         "text": json.dumps({
#             "foo": 'username:' + username
#         })
#     })
#     return redirect(home)


@login_required
def question_list(request):
    user = request.user
    questions = Question.objects.all()
    return render(request, 'pages/question_list.html', {"questions":questions, "user": user})


@login_required
def question_page(request, question_id):
    user = request.user
    question = Question.objects.get(id=question_id)
    ls = [question.choice1, question.choice2, question.choice3, question.answer]
    random.shuffle(ls)
    index = ls.index(question.answer)
    new_record = CorrectAnswer(answer_index=index)
    new_record.save()
    context = {"question_id": question.id, "record_id": new_record.id, "content": question.content, "choice1": ls[0], "choice2": ls[1],
               "choice3": ls[2], "choice4": ls[3], "user": user}
    return render(request, "pages/question_page.html", context)


@login_required
def check_answer(request):
    record_id = int(request.POST['record_id'])
    question_id = int(request.POST['question_id'])
    index = int(request.POST['index'])
    correct_answer = CorrectAnswer.objects.get(id=record_id)
    status = (correct_answer.answer_index == index)
    sentence = Question.objects.get(id=question_id).answer
    context = {"status":status, "answer": sentence}
    return render(request, 'pages/answer_status.json', context, content_type='application/json')

@login_required
def memory_game(request):
    user = request.user
    context = {'user': user}
    return render(request, "pages/memory_game.html", context)


@login_required
def random_question(request):
    question = Question.objects.order_by('?').first()
    question_id = question.id
    return question_page(request, question_id)


@login_required
def learn_page(request):
    user = request.user
    context = {'user':user}
    return render(request, "pages/learn_page.html", context)