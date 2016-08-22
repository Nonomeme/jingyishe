# coding=utf-8
import datetime

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from .forms import AnswerForm, UserForm, LoginForm, QuestionForm, SearchForm, MessageForm
from .models import Question, Answer, User, Expert, Message


# Create your views here.

def index(request):
    username = request.session.get('username', '')
    latest_questions = Question.objects.order_by("publishDate").reverse()[0:8]
    form = QuestionForm()
    if username == '':
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'form': form})

    else:
        user = User.objects.get(username=username)
        return render(request, 'home.html',
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
                redirectUrl = request.session.get('redirect_after_login', '')
                if redirectUrl == '':
                    return HttpResponseRedirect('/index/')
                else:
                    del request.session['redirect_after_login']
                    return HttpResponseRedirect(redirectUrl)
            else:
                return HttpResponseRedirect('/login')
    else:
        form = LoginForm()
        info = request.session.get('login_info', '')
        if not info == '':
            del request.session['login_info']
    return render(request, 'login.html', {'form': form, 'info': info})


def logout(request):
    del request.session['username']
    return HttpResponseRedirect('/index/')


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login')
    else:
        form = UserForm()

    return render(request, 'register.html', {'form': form})


def detail(request, question_id):
    username = request.session.get('username', '')
    question = get_object_or_404(Question, id=question_id)
    if username == '' and not question.isPublic:
        request.session['login_info'] = u'该问题仅限注册用户查看,请先登录'
        return HttpResponseRedirect('/login')

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
    return render(request, 'detail.html',
                  {'username': username, 'question': question, 'answers': answers,
                   'questionFollowers': questionFollowers, 'isFollowing': isFollowing, 'isFollowing2': isFollowing2,
                   'form': form})


def answer(request, question_id):
    username = request.session.get('username', '')
    if request.method == 'POST':
        if username == '':
            request.session['redirect_after_login'] = request.get_full_path()
            request.session['login_info'] = u'请先登陆后回答'
            return HttpResponseRedirect('/login')
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
        return render(request, 'answer.html', {'username': username, 'form': form})


def question(request):
    username = request.session.get('username', '')
    if request.method == 'POST':
        if username == '':
            request.session['redirect_after_login'] = request.get_full_path()
            request.session['login_info'] = u'请先登陆后提问'
            return HttpResponseRedirect('/login')
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
        return render(request, 'question.html', {'username': username, 'form': form})


def followQuestion(request, question_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登录'
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
        request.session['login_info'] = u'您还未登录'
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
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            questions = Question.objects.filter(
                Q(title__contains=keyword) | Q(keyword__contains=keyword)).order_by('publishDate').reverse()
            if form.cleaned_data['hasPic']:
                questions = questions.exclude(attachedFile='')
            if form.cleaned_data['isToday']:
                today = datetime.date.today()
                questions = questions.filter(publishDate__year=today.year).filter(
                    publishDate__month=today.month).filter(publishDate__day=today.day)
            # if form.cleaned_data['isHot']:

            questions = questions[:10]

        return render(request, 'newestinfo.html', {'username': username, 'questions': questions, 'form': form})
    else:
        latest_questions = Question.objects.order_by("publishDate").reverse()[0:10]
        form = SearchForm()
        return render(request, 'newestinfo.html', {'username': username, 'questions': latest_questions, 'form': form})


def aboutus(request):
    username = request.session.get('username', '')
    return render(request, 'aboutus.html', {'username': username,})


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
        messages = Message.objects.filter(receiver=publisher)
        return render(request, 'profile.html',
                      {'user': publisher, 'username': username, 'followers': count, 'questions': questions,
                       'answers': answers, 'isFollowing': isFollowing, 'messages': messages})
    else:
        if User.objects.filter(followingPerson=publisher).filter(username=username).exists():
            isFollowing = 2
        form = MessageForm()

    return render(request, 'profile.html',
                  {'user': publisher, 'username': username, 'followers': count, 'questions': questions,
                   'answers': answers, 'isFollowing': isFollowing, 'form': form})


def followUser(request, publisher_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登陆'
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    publisher = User.objects.get(id=publisher_id)
    if user.followingPerson.filter(id=publisher_id).exists():
        user.followingPerson.remove(publisher)
    else:
        user.followingPerson.add(publisher)

    return HttpResponseRedirect('/users/' + publisher_id)


def consultion(request):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登陆'
        return HttpResponseRedirect('/login')
    return render(request, 'AI.html', {'username': username})


def expert(request):
    username = request.session.get('username', '')
    experts = Expert.objects.all()[:10]
    return render(request, 'expert.html', {'username': username, 'experts': experts})


def leaveMessage(request, user_id):
    username = request.session.get('username', '')
    if request.method == 'POST':
        if username == '':
            request.session['redirect_after_login'] = request.get_full_path()
            request.session['login_info'] = u'请先登陆后留言'
            return HttpResponseRedirect('/login')
        form = MessageForm(request.POST)
        if form.is_valid():
            message = Message()
            message.message = form.cleaned_data['message']
            message.commenter = User.objects.get(username=username)
            message.receiver = User.objects.get(id=user_id)
            message.publishDate = datetime.datetime.now()
            message.isPublic = True
            if form.cleaned_data['isPublic'] == '2':
                message.isPublic = False
            message.save()

            return HttpResponseRedirect('/users/' + user_id + '/')
        else:
            return HttpResponse('fail')
    else:
        return HttpResponseRedirect('/users/' + user_id + '/')
