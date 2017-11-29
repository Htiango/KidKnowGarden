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
from kidKnowGarden.sudoku import *

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
        new_profile = Profile(user=user)
        new_room_profile = Room_Profile(user=user)
        new_profile.save()
        new_room_profile.save()
        return redirect(set_profile)
    else:
        return HttpResponse('Activation link is invalid!')


@login_required
def set_profile(request):
    context = {}
    context['profile_form'] = ProfileForm()
    if request.method == 'GET':
        return render(request, 'pages/set_profile.html', context)

    profile_form = ProfileForm(request.POST, request.FILES)
    context['profile_form'] = profile_form

    if not profile_form.is_valid():
        return render(request, 'pages/set_profile.html', context)

    profile = Profile.objects.get(user=request.user)

    # new_profile = Profile(user=request.user,
    #                       grade=profile_form.cleaned_data['grade']
    #                       )
    if profile_form.cleaned_data['grade']:
        profile.grade = profile_form.cleaned_data['grade']
    if profile_form.cleaned_data['avatar']:
        profile.avatar = profile_form.cleaned_data['avatar']
    if profile_form.cleaned_data['bio']:
        profile.bio = profile_form.cleaned_data['bio']
    profile.save()

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
def profile_page(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    question_num = len(LearnHistory.objects.filter(user=user))
    correct_num = len(LearnHistory.objects.filter(user=user, status=True))
    if question_num == 0:
        accuracy = 100
    else:
        accuracy = int(100 * correct_num / question_num)
    return render(request, 'pages/profile.html', {'profile': profile, "user": user,
                                                  "accuracy":accuracy, "question_num": question_num,
                                                  "correct_num": correct_num})


@login_required
def edit_profile_page(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    edit_profile_form = EditProfileForm(initial={'first_name': user.first_name,
                                                 'last_name': user.last_name,
                                                 'email': user.email,
                                                 'grade': profile.grade,
                                                 'bio': profile.bio})
    context = {'edit_profile_form': edit_profile_form, 'user':user}
    return render(request, 'pages/profile_edit.html', context)


@login_required
def edit_profile(request):
    if request.method == 'GET':
        return redirect(edit_profile_page)

    context = {}
    user = request.user
    context['user'] = user
    edit_profile_form = EditProfileForm(request.POST, request.FILES)
    context['edit_profile_form'] = edit_profile_form

    if not edit_profile_form.is_valid():
        return render(request, 'pages/profile_edit.html', context)

    user.first_name = edit_profile_form.cleaned_data['first_name']
    user.last_name = edit_profile_form.cleaned_data['last_name']
    user.email = edit_profile_form.cleaned_data['email']
    user.save()

    profile = Profile.objects.get(user=user)
    profile.grade = edit_profile_form.cleaned_data['grade']
    if edit_profile_form.cleaned_data['bio']:
        profile.bio = edit_profile_form.cleaned_data['bio']
    if edit_profile_form.cleaned_data['avatar']:
        profile.avatar = edit_profile_form.cleaned_data['avatar']
    profile.save()

    return redirect(profile_page)


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

# @login_required
# def room(request, id):
#     if id == 1 or id == '1':
#         raise Http404("Not found")
#     else:
#         room_object = get_object_or_404(Rooms, pk=id)
#         return render(request, 'pages/room.html', {'room': room_object, "user": request.user})

@login_required
def room(request, id, user1, user2):
    if id == 1 or id == '1':
        raise Http404("Not found")
    else:
        room_object = get_object_or_404(Rooms, pk=id)
        username = request.user.username
        if username == user1:
            opponent = User.objects.get(username=user2)
        else:
            opponent = User.objects.get(username=user1)
        return render(request, 'pages/room.html', {'room': room_object, "user": request.user, "opponent": opponent})

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
    subtitle = "Showing all the questions of all grades"
    return render(request, 'pages/question_list.html', {"questions":questions, "user": user, "subtitle":subtitle})

@login_required
def question_grade(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    questions = Question.objects.filter(grade=profile.grade)
    subtitle = "Showing all the questions of your grade."
    return render(request, 'pages/question_list.html', {"questions":questions, "user": user, "subtitle":subtitle})


@login_required
def question_history(request):
    user = request.user
    learn_history = LearnHistory.objects.filter(user=user)
    return render(request, 'pages/learning_history.html', {"learning_history": learn_history, "user":user})


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

    data = {'record_id': record_id, 'index':index}
    answer_submit_form = AnswerSubmitForm(data)
    if not answer_submit_form.is_valid():
        return render(request, 'pages/error_msg.json', {'error': "Submit has some errors"}, content_type='application/json')

    correct_answer = CorrectAnswer.objects.get(id=record_id)
    status = (correct_answer.answer_index == index)

    content = Question.objects.get(id=question_id).content
    new_learn_history = LearnHistory(question_id=question_id, content=content, user=request.user, status=status)
    new_learn_history.save()

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


@login_required
def game_page(request):
    user = request.user
    context = {'user': user}
    return render(request, "pages/game_page.html", context)


@login_required
def sudoku_game(request):
    user = request.user
    context = {'user': user}
    return render(request, "pages/sudoku_page.html", context)


@login_required
def generate_sudoku(request):
    levels = [40, 45, 50]
    level = int(request.GET.get('level'))
    empty_num = levels[level-1]
    sudoku = generate(empty_num)
    context = {"sudoku": sudoku}
    return render(request, 'pages/sudoku_new.json', context, content_type='application/json')


@login_required
def hint_sudoku(request):
    sudoku = request.GET.get('sudoku')
    (index, answer) = get_one_hint(sudoku)
    context = {"index": index, "answer": answer}
    return render(request, 'pages/sudoku_one_hint.json', context, content_type='application/json')

@login_required
def get_sudoku_solution(request):
    sudoku = request.GET.get('sudoku')
    result = get_answer(sudoku)
    context = {"sudoku": result}
    # context = {}
    return render(request, 'pages/sudoku_new.json', context, content_type='application/json')


@login_required
def check_sudoku_answer(request):
    sudoku = request.GET.get('sudoku')
    status = check_submit_answer(sudoku)
    context = {"status": status}
    return HttpResponse(status)