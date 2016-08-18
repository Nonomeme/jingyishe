# coding=utf-8
import datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from .forms import AnswerForm, UserForm, LoginForm, QuestionForm
from .models import Question, Answer, User


# Create your views here.

def index(request):
    username = request.session.get('username', '')
    user = User.objects.get(username=username)
    latest_questions = Question.objects.order_by("publishDate").reverse()[0:8]
    form = QuestionForm()
    return render(request, 'home5.html',
                  {'latest_questions': latest_questions, 'username': username, 'form': form, 'user': user})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.filter(username__exact=username, password__exact=password)
            if user:
                request.session['username'] = username
                return HttpResponseRedirect('/index/')
            else:
                return HttpResponseRedirect('/login')
    else:
        form = LoginForm()

    return render(request, 'login5.html', {'form': form})


def logout(request):
    del request.session['username']
    return HttpResponseRedirect('/index/')


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('regist success!')
    else:
        form = UserForm()

    return render(request, 'register5.html', {'form': form})


def detail(request, question_id):
    username = request.session.get('username', '')
    question = get_object_or_404(Question, id=question_id)
    questionFollowers = User.objects.filter(followingQuestion=question_id)

    # 判断登陆用户是否关注了问题和题主
    # 首先判断用户是否就是题主 isFollowing=0表示用户就是题主,1表示用户未关注,2表示已关注
    isFollowing = 1
    isFollowing2 = 1
    if question.questioner.username == username:
        isFollowing = 0
        isFollowing2 = 0
    else:
        if questionFollowers.filter(username=username).exists():  # 判断用户是否已关注这个问题
            isFollowing = 2

        publisher = question.questioner  # 判断用户是否已关注题主
        publisherFollowers = User.objects.filter(followingPerson=publisher.id)
        if publisherFollowers.filter(username=username).exists():
            isFollowing2 = 2

    form = AnswerForm()
    # if question.isSolved:
    answers = Answer.objects.filter(question=question_id)
    return render(request, 'solved1_5.html',
                  {'username': username, 'question': question, 'answers': answers,
                   'questionFollowers': questionFollowers, 'isFollowing': isFollowing, 'isFollowing2': isFollowing2,
                   'form': form})
    # else:
    #     return render(request, 'unsolved1_5.html',
    #                   {'username': username, 'question': question, 'isFollowing': isFollowing,
    #                    'isFollowing2': isFollowing2, 'form': form})


def comment(request, question_id):
    username = request.session.get('username', '')
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = Answer()
            answer.content = form.cleaned_data['content']
            answer.isPublic = True
            if form.cleaned_data['isPublic'] == '2':
                answer.isPublic = False
            answer.publishDate = datetime.datetime.now()
            answer.question = Question.objects.get(id=question_id)
            answer.answerer = User.objects.get(username=username)
            if form.cleaned_data['attachedFile'] != '':
                answer.attachedFile = form.cleaned_data['attachedFile']
            answer.save()

            return HttpResponseRedirect('/question/' + question_id + '/')
        else:
            return HttpResponse('fail')
    else:
        form = AnswerForm
        return render(request, 'answer5.html', {'username': username, 'form': form})


def question(request):
    username = request.session.get('username', '')
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if username == '':
            return HttpResponseRedirect('/login')
        if form.is_valid():
            question = Question()
            question.title = form.cleaned_data['title']
            question.description = form.cleaned_data['description']
            question.keyword = form.cleaned_data['keyword']
            if form.cleaned_data['isPublic'] == '2':
                question.isPublic = False
            question.publishDate = datetime.datetime.now()
            if form.cleaned_data['attachedFile'] != '':
                question.attachedFile = form.cleaned_data['attachedFile']
            question.questioner = User.objects.get(username=username)
            question.save()
            return HttpResponseRedirect('/index')
    else:
        form = QuestionForm()
        return render(request, 'question5.html', {'username': username, 'form': form})


def followQuestion(request, question_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    question = Question.objects.get(id=question_id)
    if user.followingQuestion.filter(id=question_id).exists():
        user.followingQuestion.remove(question)
    else:
        user.followingQuestion.add(question)

    # return render(request, 'unsolved1_5.html', {'username': username, 'question': question, 'user': user})

    return HttpResponseRedirect('/question/' + question_id)


def followPerson(request, question_id, publisher_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    publisher = User.objects.get(id=publisher_id)
    if user.followingPerson.filter(id=publisher_id).exists():
        user.followingPerson.remove(publisher)
    else:
        user.followingPerson.add(publisher)

    return HttpResponseRedirect('/question/' + question_id)


def latestQuestion(request):
    username = request.session.get('username', '')
    latest_questions = Question.objects.order_by("publishDate")[0:10]
    return render(request, 'newest_info5_1.html', {'username': username, 'questions': latest_questions})


def aboutus(request):
    username = request.session.get('username', '')
    return render(request, 'aboutus5.html', {'username': username,})


def userInfo(request, user_id):
    username = request.session.get('username', '')
    # user = User.objects.get(username=username)
    publisher = User.objects.get(id=user_id)
    followers = User.objects.filter(followingPerson=publisher)
    count = followers.count()
    questions = Question.objects.filter(questioner=publisher).order_by('publishDate').reverse()[0:3]
    answers = Answer.objects.filter(answerer=publisher).order_by('publishDate').reverse()[0:3]
    isFollowing = 1
    if publisher.username == username:
        isFollowing = 0
    else:
        if User.objects.filter(followingPerson=publisher).filter(username=username).exists():
            isFollowing = 2
    return render(request, 'myaccount5.html',
                  {'user': publisher, 'username': username, 'followers': count, 'questions': questions,
                   'answers': answers, 'isFollowing': isFollowing})


def followUser(request, publisher_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    publisher = User.objects.get(id=publisher_id)
    if user.followingPerson.filter(id=publisher_id).exists():
        user.followingPerson.remove(publisher)
    else:
        user.followingPerson.add(publisher)

    return HttpResponseRedirect('/users/' + publisher_id)
