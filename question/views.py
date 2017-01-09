# coding=utf-8
import datetime
import os
import re
import sys

import pytz
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings

from .forms import AnswerForm, UserForm, LoginForm, QuestionForm, MessageForm, SearchForm, GlobalSearchForm, \
    MessageAnswerForm, QuestionForm2, CaseForm, CourseSearchForm, UpdatePwdForm
from .models import Question, Answer, User, Expert, Message, QuestionFollow, PersonFollow, Case, CaseFollow, \
    MessageAnswer, Course

from utils.token import Token
from django.core.mail import send_mail
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from mysite.settings import page_size

token_confirm = Token(settings.SECRET_KEY)
DOMAIN = 'http://127.0.0.1:8000/'

reload(sys)
sys.setdefaultencoding('utf-8')


# Create your views here.

def index(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    latest_questions = Question.objects.order_by("publishDate").reverse()[0:8]
    latest_cases = Case.objects.order_by("date").reverse()[0:8]
    latest_users = User.objects.order_by("date").reverse()[0:8]
    latest_courses = Course.objects.order_by("publishDate").reverse()[0:8]
    form = QuestionForm()
    searchForm = GlobalSearchForm()
    if username == '':
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'userId': userId, 'form': form,
                       'searchForm': searchForm, 'latest_cases': latest_cases, 'latest_users': latest_users,
                       'courses': latest_courses})

    else:
        user = User.objects.get(username=username)
        return render(request, 'home.html',
                      {'latest_questions': latest_questions, 'username': username, 'userId': userId, 'form': form,
                       'user': user,
                       'searchForm': searchForm, 'latest_cases': latest_cases, 'latest_users': latest_users,
                       'courses': latest_courses})


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
                if not User.objects.filter(Q(username__exact=username) | Q(mail__exact=username)).exists():
                    form._errors['username'] = form.error_class([u"用户名不存在"])
                else:
                    form._errors['password'] = form.error_class([u"密码输入错误"])
                errors = form.errors
                return render(request, 'login.html', {'form': form, 'errors': errors})
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


def forgetPwd(request):
    message = ''
    if request.method == "POST":
        mail = request.POST['mail']
        if User.objects.filter(mail__exact=mail).exists():
            user = User.objects.get(mail__exact=mail)
            from_addr = 'service_csbs@163.com'
            password = 'chashuiboshi123'
            smtp_server = 'smtp.163.com'
            to_addr = mail
            subject = u'找回密码'
            token = token_confirm.generate_validate_token(user.username)
            message = u'Hi,' + user.username + '请点击连接完成用户验证:' + DOMAIN + 'updatePassword' + token
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = 'service_csbs@163.com'
            msg['To'] = mail
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            message = '请在一小时内确认邮件修改!'
        else:
            errorMsg = u'该邮箱还未注册!'
            return render(request, 'forgetPwd.html', {'message': message})

    return render(request, 'forgetPwd.html', {'message': message})


def updatePwd(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        # username = token_confirm.remove_validate_token(token)
        return render(request, 'forgetPwd.html', {
            'message': u'对不起，验证链接已经过期，请重新发送'})
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'forgetPwd.html', {'message': u"对不起，您所验证的用户不存在，请重新注册"})

    if request.method == 'GET':
        form = UpdatePwdForm()
        return render(request, 'updatePwd.html', {'form': form})
    if request.method == 'POST':
        form = UpdatePwdForm(request.POST)
        print username
        if form.is_valid():
            user.password = form.cleaned_data['password']
            user.save()
            return HttpResponseRedirect('/login/')
        else:
            errors = form.errors
            return render(request, 'updatePwd.html', {'form': form, 'errors': errors})


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # human = True
            user = User()
            user.username = form.cleaned_data['username']
            user.mail = form.cleaned_data['mail']
            user.password = form.cleaned_data['password']
            user.save()
            from_addr = 'service_csbs@163.com'
            password = 'chashuiboshi123'
            smtp_server = 'smtp.163.com'
            to_addr = user.mail
            subject = u'验证用户'
            token = token_confirm.generate_validate_token(user.username)
            message = u'Hi,' + user.username + '请点击连接完成用户验证:' + DOMAIN + 'users/activate/' + token
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = 'service_csbs@163.com'
            msg['To'] = user.mail
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            return HttpResponseRedirect('/login/')
        else:
            errors = form.errors
            return render(request, 'register.html', {'form': form, 'errors': errors})
    else:
        form = UserForm()
        return render(request, 'register.html', {'form': form})


def activateUser(request, token):
    """
    the view function is used to accomplish the user register confirm,only after input the link
    that sent to the register email,user can login the site normally.
    :param request:
    :param activate_key:the paragram is gotten by encrypting username when user register
    :return:
    """
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        return HttpResponse(u'对不起，验证链接已经过期')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(u'对不起，您所验证的用户不存在，请重新注册')
    user.isActive = True
    user.save()
    return HttpResponseRedirect('/login/')


def detail(request, question_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    question = get_object_or_404(Question, id=question_id)
    if username == '' and not question.isPublic:
        request.session['login_info'] = u'该问题仅限注册用户查看,请先登录'
        return HttpResponseRedirect('/login/')

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
        q.add(Q(keyword__icontains=keyword), Q.OR)
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
        relation = PersonFollow.objects.create(userFollower=user, followingPerson=publisher,
                                               date=datetime.date.today())
        relation.save()

    return HttpResponseRedirect('/question/' + question_id)


def latestQuestion(request):
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
            Q(title__icontains=keyword) | Q(keyword__icontains=keyword))
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
        questions = questions.order_by('answerNum')

    # page_size = 10  # 每页显示的条数
    # # after_range_num = 5
    # # before_range_num = 6
    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(questions, page_size)  # 分页器
    try:
        questions = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        questions = paginator.page(1)
    # if page >= after_range_num:
    #     page_range = paginator.page_range[page-after_range_num:page+before_range_num] #页码的列表
    # else:
    #     page_range = paginator.page_range[0:int(page)+before_range_num]


    # questions = questions[:10]

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
        newslist.remove(newslist[len(newslist) - 1])

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
    experts = Expert.objects.all().order_by('h_index').reverse()
    keyword = ''
    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        experts = experts.filter(
            Q(name__icontains=keyword) | Q(university__icontains=keyword) | Q(tag__icontains=keyword))

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(experts, page_size)  # 分页器
    try:
        experts = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        experts = paginator.page(1)

    form = SearchForm({'keyword': keyword, 'isToday': False, 'isHot': False})
    if not form.is_valid():
        form = SearchForm()
    return render(request, 'expert.html',
                  {'username': username, 'userId': userId, 'experts': experts, 'form': form})


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
            message.publishDate = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
            message.isPublic = True
            if request.POST['isPublic'] == 'False':
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
    cases = Case.objects.all().order_by('date').reverse()
    keyword = ''
    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        cases = cases.filter(Q(title__icontains=keyword) | Q(keyword__icontains=keyword) | Q(caseType=keyword))
    if 'category' in request.GET:
        category = request.GET['category']
        if category != u'0':
            direction = request.GET['direction']
            caseType = category + '案例:' + direction
            print caseType
            cases = cases.filter(caseType__icontains=caseType)

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(cases, page_size)  # 分页器
    try:
        cases = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        cases = paginator.page(1)

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
    prefix = os.getcwd() + '/media/question/'
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
    prefix = os.getcwd() + '/media/answer/'
    fileName = os.path.split(answer.attachedFile.name)[1]
    response = StreamingHttpResponse(file_iterator(prefix + fileName))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)

    return response


def downloadCase(request, case_id):
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

    case = Case.objects.get(id=case_id)
    prefix = os.getcwd() + '/media/case/'
    fileName = os.path.split(case.attachedDescription.name)[1]
    response = StreamingHttpResponse(file_iterator(prefix + fileName))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)

    return response


def downloadSolution(request, case_id):
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

    case = Case.objects.get(id=case_id)
    prefix = os.getcwd() + '/media/caseSolution/'
    fileName = os.path.split(case.attachedSolution.name)[1]
    response = StreamingHttpResponse(file_iterator(prefix + fileName))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(fileName)

    return response


def relatedQuestions(request, question_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    question = get_object_or_404(Question, id=question_id)
    searchForm = GlobalSearchForm()
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
        q.add(Q(keyword__icontains=keyword), Q.OR)
    relatedQuestions = Question.objects.filter(q).exclude(id=question_id).order_by('answerNum').reverse()

    # try:
    #     page = int(request.GET.get("page", 1))
    #     if page < 1:
    #         page = 1
    # except ValueError:
    #     page = 1
    # paginator = Paginator(relatedQuestions, page_size)  # 分页器
    # try:
    #     relatedQuestions = paginator.page(page)
    # except(EmptyPage, InvalidPage, PageNotAnInteger):
    #     relatedQuestions = paginator.page(1)

    return render(request, 'related_question.html',
                  {'username': username, 'userId': userId, 'question': question,
                   'relatedQuestions': relatedQuestions,
                   'isFollowing': isFollowing, 'isFollowing2': isFollowing2, 'searchForm': searchForm})


def myquestions(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    questions = Question.objects.filter(questioner=user).order_by('publishDate').reverse()

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(questions, page_size)  # 分页器
    try:
        questions = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        questions = paginator.page(1)

    return render(request, 'myquestions.html',
                  {'username': username, 'userId': userId, 'user': user, 'questions': questions})


def myanswers(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    answers = Answer.objects.filter(answerer=user).order_by('publishDate').reverse()

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(answers, page_size)  # 分页器
    try:
        answers = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        answers = paginator.page(1)

    return render(request, 'myanswers.html',
                  {'username': username, 'userId': userId, 'user': user, 'answers': answers})


def mycases(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    # cases = user.followingCase.all().order_by('publishDate').reverse()
    cases = CaseFollow.objects.filter(caseFollower=user).order_by('date').reverse()

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(cases, page_size)  # 分页器
    try:
        cases = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        cases = paginator.page(1)

    return render(request, 'mycases.html', {'username': username, 'userId': userId, 'user': user, 'cases': cases})


def mysharings(request, user_id):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    user = User.objects.get(id=user_id)
    # cases = user.followingCase.all().order_by('publishDate').reverse()
    cases = Case.objects.filter(uploader=user).order_by('date').reverse()

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(cases, page_size)  # 分页器
    try:
        cases = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        cases = paginator.page(1)

    return render(request, 'mysharings.html', {'username': username, 'userId': userId, 'user': user, 'cases': cases})


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

        attachedFile = request.FILES.get('attachedFile', None)
        if attachedFile:
            question.attachedFile = attachedFile

        question.attachedDescription = request.POST['attachedDescription']

        if request.POST['isSolved'] == 'True':
            question.isSolved = True
        else:
            question.isSolved = False
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
            file_data = {
                'attachedFile': SimpleUploadedFile(question.attachedFile.name, question.attachedFile.read())}
            form = QuestionForm2(data, file_data)
            # print form.is_bound()
        else:
            form = QuestionForm2(data)
        searchForm = GlobalSearchForm()
        return render(request, 'updateQuestion.html',
                      {'username': username, 'userId': userId, 'question': question, 'form': form,
                       'searchForm': searchForm, 'isSolved': question.isSolved})


def search(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    keyword = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        cases = Case.objects.filter(Q(title__icontains=keyword) | Q(keyword__icontains=keyword))[:5]
        questions = Question.objects.filter(Q(title__icontains=keyword) | Q(keyword__icontains=keyword)).order_by(
            'publishDate').reverse()[:5]
        experts = Expert.objects.filter(tag__icontains=keyword)[:5]
        courses = Course.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))[:5]
        searchForm = GlobalSearchForm({'keyword': keyword})
        return render(request, 'globalSearch.html',
                      {'username': username, 'userId': userId, 'questions': questions, 'experts': experts,
                       'cases': cases, 'courses': courses,
                       'searchForm': searchForm})
    else:
        searchForm = GlobalSearchForm()
        return render(request, 'globalSearch.html',
                      {'username': username, 'userId': userId, 'searchForm': searchForm})


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


def courses(request):
    username = request.session.get('username', '')
    userId = request.session.get('userId', '')
    courses = Course.objects.all()
    keyword = ''
    data = {}

    if 'keyword' in request.GET:  # GET是一个dict，使用文本框的name作为key
        keyword = request.GET['keyword']
        courses = courses.filter(
            Q(title__icontains=keyword) | Q(description__icontains=keyword) | Q(university__icontains=keyword))
        data.update({'keyword': keyword})

    if 'language' in request.GET:
        if request.GET['language'] == '1':
            courses = courses.filter(Q(language=1) | Q(language=3))
            language = '1'
        elif request.GET['language'] == '2':
            courses = courses.filter(Q(language=2) | Q(language=3))
            language = '2'
        data.update({'language': language})

    # if 'time' in request.GET:
    #     today = datetime.date.today()
    #     print today
    #     if request.GET['time'] == '1':
    #         courses = courses.filter(
    #             Q(publishDate__year=today.year) & Q(publishDate__month=today.month) & Q(publishDate__day=today.day))
    #         time = '1'
    #     elif request.GET['time'] == '2':
    #         courses = courses.filter(Q(courseDate__gt=(today - datetime.timedelta(7))) & Q(courseDate__lte=today))
    #         time = '2'
    #     elif request.GET['time'] == '3':
    #         courses = courses.filter(Q(courseDate__lt=(today + datetime.timedelta(7))) & Q(courseDate__gt=today))
    #         time = '3'
    #     data.update({'time': time})

    if 'order' in request.GET:
        if request.GET['order'] == '1':
            courses = courses.order_by('publishDate').reverse()
            order = '1'
        if request.GET['order'] == '2':
            courses = courses.order_by('courseDate').reverse()
            order = '2'
        if request.GET['order'] == '3':
            courses = courses.order_by('popularity').reverse()
            order = '3'
        data.update({'order': order})

    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(courses, 5)  # 分页器
    try:
        courses = paginator.page(page)
    except(EmptyPage, InvalidPage, PageNotAnInteger):
        courses = paginator.page(1)

    form = CourseSearchForm(data)
    if not form.is_valid():
        form = CourseSearchForm()

    return render(request, 'courses.html',
                  {'username': username, 'userId': userId, 'form': form, 'courses': courses})


def userTag(request, user_id):
    user = User.objects.get(id=user_id)
    if user:
        user.tag = request.POST['tag']
        user.save()
    return HttpResponseRedirect('/users/' + user_id + '/')
