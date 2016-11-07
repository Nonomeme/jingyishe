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

from .forms import AnswerForm, UserForm, LoginForm, QuestionForm, MessageForm, SearchForm, GlobalSearchForm, \
    MessageAnswerForm, QuestionForm2, CaseForm

QuestionForm2
from .models import Question, Answer, User, Expert, Message, QuestionFollow, PersonFollow, Case, CaseFollow, \
    MessageAnswer

reload(sys)
sys.setdefaultencoding('utf-8')


# Create your views here.

def index(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    latest_questions = Question.objects.order_by("publishDate").reverse()[0:8]
    latest_cases = Case.objects.order_by("date").reverse()[0:8]
    latest_users = User.objects.order_by("date").reverse()[0:8]
    form = QuestionForm()
    searchForm = GlobalSearchForm()
    if username == '':
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'userId': userId, 'form': form,
                       'searchForm': searchForm, 'latest_cases': latest_cases, 'latest_users': latest_users})

    else:
        user = User.objects.get(username=username)
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'userId': userId, 'form': form,
                       'user': user,
                       'searchForm': searchForm, 'latest_cases': latest_cases, 'latest_users': latest_users})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username.rfind('@') == -1:
                user = User.objects.filter(username__exact=username, password__exact=password)
            else:
                user = User.objects.filter(mail__exact=username, password__exact=password)
            if user:
                request.session['username'] = user[0].username
                request.session['userId'] = user[0].id
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
    del request.session['userId']
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
    userId = request.session.get('userId', '')
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
    answers = Answer.objects.filter(question=question_id).order_by('grade').reverse()
    # 排除仅题主可见的回答
    if not isFollowing == 0:
        answers.exclude(isPublic=False)
    keywords = question.keyword.split(';')
    q = Q()
    for keyword in keywords:
        q.add(Q(keyword__contains=keyword), Q.OR)
    relatedQuestions = Question.objects.filter(q).exclude(id=question_id)
    return render(request, 'detail.html',
                  {'username': username, 'userId': userId, 'question': question, 'answers': answers,
                   'relatedQuestions': relatedQuestions,
                   'questionFollowers': questionFollowers, 'isFollowing': isFollowing, 'isFollowing2': isFollowing2,
                   'form': form, 'searchForm': searchForm})


def answer(request, question_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
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
        return render(request, 'answer.html', {'username': username, 'userId': userId, 'form': form})


def question(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    if request.method == 'POST':
        if username == '':
            request.session['redirect_after_login'] = request.get_full_path()
            request.session['login_info'] = u'请先登陆后提问'
            return HttpResponseRedirect('/login')
        form = QuestionForm(request.POST, request.FILES)
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
        form = QuestionForm2()
        return render(request, 'question.html', {'username': username, 'userId': userId, 'form': form})


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
    userId = request.session.get('userId', '')
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
    return render(request, 'newestinfo.html',
                  {'username': username, 'userId': userId, 'questions': questions, 'form': form})


def aboutus(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    return render(request, 'aboutus.html', {'username': username, 'userId': userId,})


def userInfo(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    # user = User.objects.get(username=username)
    publisher = User.objects.get(id=user_id)
    followers = User.objects.filter(followingPerson=publisher)
    count = followers.count()
    questions = Question.objects.filter(questioner=publisher).order_by('publishDate').reverse()
    answers = Answer.objects.filter(answerer=publisher).order_by('publishDate').reverse()
    answerNum = answers.count()
    answers = answers[:3]
    followingQuestions = QuestionFollow.objects.filter(questionFollower=user_id).order_by('date').reverse()[:5]
    followingPersons = PersonFollow.objects.filter(userFollower=user_id).order_by('date').reverse()[:5]
    cases = Case.objects.filter(uploader=publisher).order_by('date').reverse()[:5]
    tmplist, newslist, questionlist, personlist, caselist = [], [], [], [], []
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

    for case in cases:
        delta = today - case.date.date()
        caselist.append({'name': case.title,
                         'timeDelta': int(delta.total_seconds() / 86400),
                         'type': 3,
                         'url': case.id})

    i = j = 0

    while i < len(questionlist) and j < len(personlist):
        if questionlist[i]['timeDelta'] < personlist[j]['timeDelta']:
            tmplist.append(questionlist[i])
            i += 1
        else:
            tmplist.append(personlist[j])
            j += 1

    while i < len(questionlist):
        tmplist.append(questionlist[i])
        i += 1
    while j < len(personlist):
        tmplist.append(personlist[j])
        j += 1

    i = j = 0
    while len(tmplist) > 5:
        tmplist.remove(len(tmplist) - 1)
    while i < len(tmplist) and j < len(caselist):
        if tmplist[i]['timeDelta'] < caselist[j]['timeDelta']:
            newslist.append(tmplist[i])
            i += 1
        else:
            newslist.append(caselist[j])
            j += 1
    while i < len(tmplist):
        newslist.append(tmplist[i])
        i += 1
    while j < len(caselist):
        newslist.append(caselist[j])
        j += 1
    while len(newslist) > 5:
        newslist.remove(len(newslist) - 1)

    print newslist
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
                      {'user': publisher, 'username': username, 'userId': userId, 'followers': count,
                       'questions': questions,
                       'answers': answers, 'isFollowing': isFollowing, 'messages': messages, 'num': num,
                       'answerNum': answerNum, 'following': newslist})
    else:
        if User.objects.filter(followingPerson=publisher).filter(username=username).exists():
            isFollowing = 2
        form = MessageForm()

    return render(request, 'profile.html',
                  {'user': publisher, 'username': username, 'userId': userId, 'followers': count,
                   'questions': questions,
                   'answers': answers, 'isFollowing': isFollowing, 'form': form, 'num': num, 'answerNum': answerNum,
                   'following': newslist})


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
    userId = request.session.get('userId', '')
    if username == '':
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登陆'
        return HttpResponseRedirect('/login')
    return render(request, 'AI.html', {'username': username})


def expert(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    experts = Expert.objects.all()
    keyword = ''
    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        experts = experts.filter(Q(name__contains=keyword) | Q(university__contains=keyword) | Q(tag__contains=keyword))

    experts = experts[:10]

    form = SearchForm({'keyword': keyword, 'isToday': False, 'isHot': False})
    if not form.is_valid():
        form = SearchForm()
    return render(request, 'expert.html', {'username': username, 'userId': userId, 'experts': experts, 'form': form})


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


def answerMessage(request, user_id, message_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    message = Message.objects.get(id=message_id)
    if request.method == 'POST':
        form = MessageAnswerForm(request.POST)
        if form.is_valid():
            answer = MessageAnswer()
            answer.answer = form.cleaned_data['answer']
            answer.message = message
        return HttpResponseRedirect('/users/' + user_id + '/')
    else:
        user = User.objects.get(id=user_id)
        form = MessageAnswerForm()
        return render(request, 'mymessage.html',
                      {'username': username, 'userId': userId, 'user': user, 'message': message, 'form': form})


def case(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    cases = Case.objects.all()
    keyword = ''
    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        cases = cases.filter(Q(title__contains=keyword) | Q(keyword__contains=keyword) | Q(caseType=keyword))
    if 'category' in request.GET:
        category = request.GET['category']
        if category != u'0':
            direction = request.GET['direction']
            caseType = category + '案例:' + direction
            print caseType
            cases = cases.filter(caseType__contains=caseType)

    cases = cases.order_by('date').reverse()[:10]

    form = SearchForm({'keyword': keyword, 'isToday': False, 'isHot': False})
    if not form.is_valid():
        form = SearchForm()
    return render(request, 'case.html', {'username': username, 'userId': userId, 'cases': cases, 'form': form})


def caseDetail(request, case_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    case = Case.objects.get(id=case_id)
    isFollowing = False

    if not username == '':
        user = User.objects.get(username=username)
        if user.followingCase.filter(id=case_id).exists():
            isFollowing = True

    return render(request, 'caseDetail.html',
                  {'username': username, 'userId': userId, 'case': case, 'isFollowing': isFollowing})


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
    userId = request.session.get('userId', '')
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
                  {'username': username, 'userId': userId, 'question': question, 'relatedQuestions': relatedQuestions,
                   'isFollowing': isFollowing, 'isFollowing2': isFollowing2,})


def myquestions(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    questions = Question.objects.filter(questioner=user).order_by('publishDate').reverse()
    return render(request, 'myquestions.html',
                  {'username': username, 'userId': userId, 'user': user, 'questions': questions})


def myanswers(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    answers = Answer.objects.filter(answerer=user).order_by('publishDate').reverse()
    return render(request, 'myanswers.html', {'username': username, 'userId': userId, 'user': user, 'answers': answers})


def mycases(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    # cases = user.followingCase.all().order_by('publishDate').reverse()
    cases = CaseFollow.objects.filter(caseFollower=user)
    return render(request, 'mycases.html', {'username': username, 'userId': userId, 'user': user, 'cases': cases})


def updateQuestion(request, question_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(username=username)
    if request.method == 'POST':
        question = Question.objects.get(id=question_id)
        question.description = request.POST['description']
        question.keyword = request.POST['keyword']
        if request.POST['isPublic'] == '2':
            question.isPublic = False
        else:
            question.isPublic = True
        if question.attachedFile == '':
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
        if not question.attachedFile == '':
            file_data = {'attachedFile': SimpleUploadedFile(question.attachedFile.name, question.attachedFile.read())}
            form = QuestionForm2(data, file_data)
            # print form.is_bound()
        else:
            form = QuestionForm2(data)
        searchForm = GlobalSearchForm()
        return render(request, 'updateQuestion.html',
                      {'username': username, 'userId': userId, 'question': question, 'form': form,
                       'searchForm': searchForm})


def search(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    keyword = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        cases = Case.objects.filter(Q(title__contains=keyword) | Q(keyword__contains=keyword))[:5]
        questions = Question.objects.filter(Q(title__contains=keyword) | Q(keyword__contains=keyword)).order_by(
            'publishDate').reverse()[:5]
        experts = Expert.objects.filter(tag__contains=keyword)[:5]
        searchForm = GlobalSearchForm({'keyword': keyword})
        return render(request, 'globalSearch.html',
                      {'username': username, 'userId': userId, 'questions': questions, 'experts': experts,
                       'cases': cases,
                       'searchForm': searchForm})
    else:
        searchForm = GlobalSearchForm()
        return render(request, 'globalSearch.html', {'username': username, 'userId': userId, 'searchForm': searchForm})


def closeQuestion(request, question_id):
    question = Question.objects.get(id=question_id)
    question.isSolved = True
    question.save()

    return HttpResponseRedirect('/question/' + question_id + '/')


def grade(request, answer_id):
    username = request.session.get('username', '')
    if username == "":
        request.session['redirect_after_login'] = request.get_full_path()
        request.session['login_info'] = u'您还未登陆'
        return HttpResponseRedirect('/login')
    user = User.objects.get(username=username)
    answer = Answer.objects.get(id=answer_id)
    if user.gradeAnswer.all().filter(id=answer_id).exists():
        user.gradeAnswer.remove(answer)
        answer.grade -= 1
        answer.save()
    else:
        user.gradeAnswer.add(answer)
        answer.grade += 1
        answer.save()

    return HttpResponseRedirect('/question/' + str(answer.question_id) + '/')


def addCase(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    if request.method == 'POST':
        # print request.POST
        if username == "":
            request.session['redirect_after_login'] = request.get_full_path()
            request.session['login_info'] = u'您还未登陆'
            return HttpResponseRedirect('/login')
        user = User.objects.get(username=username)
        form = CaseForm(request.POST, request.FILES)
        if form.is_valid():
            case = Case()
            case.title = form.cleaned_data['title']
            case.questionDescription = form.cleaned_data['questionDescription']
            case.dataDescription = form.cleaned_data['dataDescription']
            case.solution = form.cleaned_data['solution']
            case.keyword = form.cleaned_data['keyword']
            case.uploader = user
            case.caseType = form.cleaned_data['category'] + '案例:' + request.POST['direction']
            # print case.caseType
            if form.cleaned_data['attachedDescription'] != '':
                case.attachedDescription = form.cleaned_data['attachedDescription']
            if form.cleaned_data['attachedSolution'] != '':
                case.attachedSolution = form.cleaned_data['attachedSolution']
            case.date = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
            case.save()
            return HttpResponseRedirect('/case/')
        else:
            print form.errors

    else:
        form = CaseForm()
        # print form
    return render(request, 'caseShare.html', {'username': username, 'userId': userId, 'form': form})
