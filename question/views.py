# coding=utf-8
import datetime
import os
import re
import sys

import pytz
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404

from .forms import AnswerForm, UserForm, LoginForm, QuestionForm, MessageForm, SearchForm, GlobalSearchForm
from .models import Question, Answer, User, Expert, Message, QuestionFollow, PersonFollow, Case, CaseFollow

reload(sys)
sys.setdefaultencoding('utf-8')


# Create your views here.

def index(request):
    username = request.session.get('username', '')
    latest_questions = Question.objects.order_by("publishDate").reverse()[0:8]
    form = QuestionForm()
    searchForm = GlobalSearchForm()
    if username == '':
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'form': form,
                       'searchForm': searchForm})

    else:
        user = User.objects.get(username=username)
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'form': form, 'user': user,
                       'searchForm': searchForm})


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
    searchForm = GlobalSearchForm()
    # if question.isSolved:
    answers = Answer.objects.filter(question=question_id)
    keywords = question.keyword.split(';')
    q = Q()
    for keyword in keywords:
        q.add(Q(keyword__contains=keyword), Q.OR)
    relatedQuestions = Question.objects.filter(q).exclude(id=question_id)
    return render(request, 'detail.html',
                  {'username': username, 'question': question, 'answers': answers, 'relatedQuestions': relatedQuestions,
                   'questionFollowers': questionFollowers, 'isFollowing': isFollowing, 'isFollowing2': isFollowing2,
                   'form': form, 'searchForm': searchForm})


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
            answer.publishDate = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
            answer.question = Question.objects.get(id=question_id)
            answer.answerer = User.objects.get(username=username)
            if form.cleaned_data['attachedFile'] != '':
                answer.attachedFile = form.cleaned_data['attachedFile']
            answer.save()

            question = Question.objects.get(id=question_id)
            question.answerNum += 1
            question.save()

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
            question.publishDate = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
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
        relation = QuestionFollow.objects.get(questionFollower=user, followingQuestion=question)
        relation.delete()
    else:
        relation = QuestionFollow.objects.create(questionFollower=user, followingQuestion=question,
                                                 date=datetime.date.today())
        relation.save()

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
        relation = PersonFollow.objects.get(userFollower=user, followingPerson=publisher)
        relation.delete()
    else:
        relation = PersonFollow.objects.create(userFollower=user, followingPerson=publisher, date=datetime.date.today())
        relation.save()

    return HttpResponseRedirect('/question/' + question_id)


def latestQuestion(request, type="0"):
    username = request.session.get('username', '')
    questions = Question.objects.all().order_by('publishDate').reverse()
    keyword = ''
    # hasPic = False
    isToday = False
    isHot = False

    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        questions = questions.filter(
            Q(title__contains=keyword) | Q(keyword__contains=keyword))
        # if 'hasPic' in request.GET:
        #     hasPic = True
        #     questions = questions.exclude(attachedFile='')
    if 'isToday' in request.GET:
        isToday = True
        today = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        questions = questions.filter(
            Q(publishDate__year=today.year) & Q(publishDate__month=today.month) & Q(publishDate__day=today.day))

    if 'isHot' in request.GET:
        isHot = True

    questions = questions[:10]

    form = SearchForm({'keyword': keyword, 'isToday': isToday, 'isHot': isHot})
    if not form.is_valid():
        form = SearchForm()
    return render(request, 'newestinfo.html', {'username': username, 'questions': questions, 'form': form})


def aboutus(request):
    username = request.session.get('username', '')
    return render(request, 'aboutus.html', {'username': username,})


def userInfo(request, user_id):
    username = request.session.get('username', '')
    # user = User.objects.get(username=username)
    publisher = User.objects.get(id=user_id)
    followers = User.objects.filter(followingPerson=publisher)
    count = followers.count()
    questions = Question.objects.filter(questioner=publisher).order_by('publishDate').reverse()
    answers = Answer.objects.filter(answerer=publisher).order_by('publishDate').reverse()
    answerNum = answers.count()
    answers = answers[:3]
    followingQuestions = QuestionFollow.objects.filter(questionFollower=user_id).order_by('date').reverse()[:3]
    followingPersons = PersonFollow.objects.filter(userFollower=user_id).order_by('date').reverse()[:3]
    followinglist, questionlist, personlist = [], [], []
    today = datetime.date.today()
    for question in followingQuestions:
        delta = today - question.date
        questionlist.append({'name': question.followingQuestion.title,
                             'timeDelta': int(delta.total_seconds() / 86400),
                             'type': 1,
                             'url': question.followingQuestion.id})

    for person in followingPersons:
        delta = today - person.date
        personlist.append({'name': person.followingPerson.username,
                           'timeDelta': int(delta.total_seconds() / 86400),
                           'type': 2,
                           'url': person.followingPerson.id})
    i = j = 0
    while i < len(questionlist) and j < len(personlist):
        if questionlist[i]['timeDelta'] < personlist[j]['timeDelta']:
            followinglist.append(questionlist[i])
            i += 1
        else:
            followinglist.append(personlist[j])
            j += 1

    while i < len(questionlist):
        followinglist.append(questionlist[i])
        i += 1
    while j < len(personlist):
        followinglist.append(personlist[j])
        j += 1
    # for question in followingQuestions:
    #     for person in followingPersons:
    #         if question.date < person.date:
    #             delta = today - question.date
    #             followinglist .append(
    #                 {'name': question.followingQuestion.title,
    #                  'timeDelta': int(delta.total_seconds()/86400),
    #                  'type': 1,
    #                  'url': question.followingQuestion.id})
    #             break
    #         else:
    #             if
    #             delta = today - person.date
    #             followinglist.append({
    #                 'name': person.followingPerson.username,
    #                 'timeDelta': int(delta.total_seconds()/86400),
    #                 'type': 2,
    #                 'url': person.followingPerson.id
    #             })

    followingCases = publisher.followingCase.all()
    num = followingCases.count()
    isFollowing = 1
    if publisher.username == username:
        isFollowing = 0
        messages = Message.objects.filter(receiver=publisher)
        return render(request, 'profile.html',
                      {'user': publisher, 'username': username, 'followers': count, 'questions': questions,
                       'answers': answers, 'isFollowing': isFollowing, 'messages': messages, 'num': num,
                       'answerNum': answerNum, 'following': followinglist})
    else:
        if User.objects.filter(followingPerson=publisher).filter(username=username).exists():
            isFollowing = 2
        form = MessageForm()

    return render(request, 'profile.html',
                  {'user': publisher, 'username': username, 'followers': count, 'questions': questions,
                   'answers': answers, 'isFollowing': isFollowing, 'form': form, 'num': num, 'answerNum': answerNum,
                   'following': followinglist})


def followUser(request, publisher_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登陆'
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    publisher = User.objects.get(id=publisher_id)
    if user.followingPerson.filter(id=publisher_id).exists():
        relation = PersonFollow.objects.get(userFollower=user, followingPerson=publisher)
        relation.delete()
    else:
        relation = PersonFollow.objects.create(userFollower=user, followingPerson=publisher)
        relation.save()

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
            message.publishDate = datetime.datetime.now(datetime.datetime.now)
            message.isPublic = True
            if form.cleaned_data['isPublic'] == '2':
                message.isPublic = False
            message.save()

            return HttpResponseRedirect('/users/' + user_id + '/')
        else:
            return HttpResponse('fail')
    else:
        return HttpResponseRedirect('/users/' + user_id + '/')


def case(request):
    username = request.session.get('username', '')
    cases = Case.objects.all()
    keyword = ''

    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        cases = cases.filter(Q(title__contains=keyword) | Q(keyword__contains=keyword))

    cases = cases[:10]

    form = SearchForm({'keyword': keyword, 'isToday': False, 'isHot': False})
    if not form.is_valid():
        form = SearchForm()
    return render(request, 'case.html', {'username': username, 'cases': cases, 'form': form})


def caseDetail(request, case_id):
    username = request.session.get('username', '')
    case = Case.objects.get(id=case_id)
    isFollowing = False

    if not username == '':
        user = User.objects.get(username=username)
        if user.followingCase.filter(id=case_id).exists():
            isFollowing = True

    return render(request, 'caseDetail.html', {'username': username, 'case': case, 'isFollowing': isFollowing})


def caseFollow(request, case_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登录'
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    case = Case.objects.get(id=case_id)

    if user.followingCase.filter(id=case_id).exists():
        relation = CaseFollow.objects.get(caseFollower=user, followingCase=case)
        relation.delete()
    else:
        relation = CaseFollow.objects.create(caseFollower=user, followingCase=case,
                                             date=datetime.date.today())
        relation.save()

    return HttpResponseRedirect('/case/' + case_id)


def download(request, question_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'请先登录后下载'
        return HttpResponseRedirect('/login')

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    question = Question.objects.get(id=question_id)
    prefix = os.getcwd() + '/media/'
    fileName = os.path.split(question.attachedFile.name)[1]
    response = StreamingHttpResponse(file_iterator(prefix + fileName))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)

    return response


def downloadAnswer(request, answer_id):
    username = request.session.get('username', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'请先登录后下载'
        return HttpResponseRedirect('/login')

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    answer = Answer.objects.get(id=answer_id)
    prefix = os.getcwd() + '/media/'
    fileName = os.path.split(answer.attachedFile.name)[1]
    response = StreamingHttpResponse(file_iterator(prefix + fileName))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)

    return response


def relatedQuestions(request, question_id):
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

    # keywords = question.keyword.split(';')
    keywords = re.split(r'[,;]', question.keyword)
    q = Q()
    for keyword in keywords:
        q.add(Q(keyword__contains=keyword), Q.OR)
    relatedQuestions = Question.objects.filter(q).exclude(id=question_id)

    return render(request, 'related_question.html',
                  {'username': username, 'question': question, 'relatedQuestions': relatedQuestions,
                   'isFollowing': isFollowing, 'isFollowing2': isFollowing2,})


def myquestions(request, user_id):
    username = request.session.get('username', '')
    user = User.objects.get(id=user_id)
    questions = Question.objects.filter(questioner=user).order_by('publishDate').reverse()
    return render(request, 'myquestions.html', {'username': username, 'user': user, 'questions': questions})


def myanswers(request, user_id):
    username = request.session.get('username', '')
    user = User.objects.get(id=user_id)
    answers = Answer.objects.filter(answerer=user).order_by('publishDate').reverse()
    return render(request, 'myanswers.html', {'username': username, 'user': user, 'answers': answers})


def mycases(request, user_id):
    username = request.session.get('username', '')
    user = User.objects.get(id=user_id)
    # cases = user.followingCase.all().order_by('publishDate').reverse()
    cases = CaseFollow.objects.filter(caseFollower=user)
    return render(request, 'mycases.html', {'username': username, 'user': user, 'cases': cases})


def updateQuestion(request, question_id):
    username = request.session.get('username', '')
    user = User.objects.get(username=username)
    if request.method == 'POST':
        question = Question.objects.get(id=question_id)
        question.description = request.POST['description']
        question.keyword = request.POST['keyword']
        if request.POST['isPublic'] == '2':
            question.isPublic = False
        else:
            question.isPublic = True
        question.attachedFile = request.FILES.get('attachedFile', None)
        question.attachedDescription = request.POST['attachedDescription']
        question.save()
        return HttpResponseRedirect('/users/' + str(user.id) + '/questions/')

        # # print request.FILES.get('attachedFile', None)
        # form = QuestionForm(
        #     {'title': question.title, 'description': request.POST['description'], 'keyword': request.POST['keyword'],
        #      'attachedFile': request.FILES.get('attachedFile', None), 'isPublic': request.POST['isPublic'],
        #      'attachedDescription': request.POST['attachedDescription']})
        # print request.FILES.get('attachedFile', None)
        # if form.is_valid():
        #     print form.cleaned_data
        #     question = Question.objects.get(id=question_id)
        #     question.description = form.cleaned_data['description']
        #     question.keyword = form.cleaned_data['keyword']
        #     if form.cleaned_data['isPublic'] == '2':
        #         question.isPublic = False
        #     else:
        #         question.isPublic = True
        #     if form.cleaned_data['attachedFile'] != '':
        #         question.attachedFile = form.cleaned_data['attachedFile']
        #     question.attachedDescription = form.cleaned_data['attachedDescription']
        #     question.save()
        #     return HttpResponseRedirect('/users/' + str(user.id) + '/questions/')
        # else:
        #     return HttpResponseRedirect(request.path)
    else:
        question = Question.objects.get(id=question_id)
        if question.isPublic:
            choice = 1
        else:
            choice = 2
        data = {'title': question.title, 'description': question.description, 'keyword': question.keyword,
                'isPublic': choice, 'attachedDescription': question.attachedDescription}
        file_data = {'attachedFile': SimpleUploadedFile(question.attachedFile.name, question.attachedFile.read())}

        form = QuestionForm(data, file_data)
        # if form.is_valid():
        #     print 'valid'
        #     print form.cleaned_data['attachedFile']
        # else:
        #     print 'wrong'
        return render(request, 'updateQuestion.html', {'username': username, 'question': question, 'form': form})


def search(request):
    username = request.session.get('username', '')
    keyword = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        cases = Case.objects.filter(Q(title__contains=keyword) | Q(keyword__contains=keyword))[:5]
        questions = Question.objects.filter(Q(title__contains=keyword) | Q(keyword__contains=keyword)).order_by(
            'publishDate').reverse()[:5]
        experts = Expert.objects.filter(tag__contains=keyword)[:5]
        searchForm = GlobalSearchForm({'keyword': keyword})
        return render(request, 'globalSearch.html',
                      {'username': username, 'questions': questions, 'experts': experts, 'cases': cases,
                       'searchForm': searchForm})
    else:
        searchForm = GlobalSearchForm()
        return render(request, 'globalSearch.html', {'username': username, 'searchForm': searchForm})
