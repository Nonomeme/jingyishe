# coding:utf-8

import os, sys
import xlrd, datetime, time
from xlrd import xldate_as_tuple

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# sys.path.insert(0,'/Users/project/jingyishe/')

# print os.path.abspath(os.path.curdir)
# from question import models as qm
# import question
# from question.models import Case, User


# 初始化django环境
# from mysite.wsgi import *


'''
Django 版本大于等于1.7的时候，需要加上下面两句
import django
django.setup()
否则会抛出错误 django.core.exceptions.AppRegistryNotReady: Models aren't loaded yet.
'''

import django

django.setup()

from question.models import *


def caseDump():
    f = xlrd.open_workbook('data/Case.xls')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    caseList = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            title = row[1]
            questionDescription = row[2]
            dataDescription = row[3]
            keyword = row[4]
            solution = row[5]
            source = row[6]
            reference = row[7]
            caseType = row[8]
            date = datetime.datetime.now()
            uploader = User.objects.get(id=1)
            case = Case(title=title, questionDescription=questionDescription,
                        dataDescription=dataDescription, keyword=keyword,
                        solution=solution, source=source, reference=reference,
                        caseType=caseType, date=date, uploader=uploader)
            caseList.append(case)
    Case.objects.bulk_create(caseList)
    print('case done')


def expertDump():
    f = xlrd.open_workbook('data/Expert.xlsx')

    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols

    expertList = []

    # row = table.row_values(1)
    # name = row[0]
    # university = row[2]
    # department = row[3]
    # tag = row[4]
    # link = row[5]
    # h_index = row[6]
    # course = row[7]
    #
    # print name
    # print university
    # print department
    # print tag
    # print link
    # print h_index
    # print course
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            name = row[0]
            university = row[2]
            department = row[3]
            tag = row[4]
            link = row[5]
            h_index = row[6]
            try:
                h_index = int(h_index)
            except:
                h_index = 0
            course = row[7]
            expert = Expert(name=name, university=university, department=department,
                            tag=tag, link=link, h_index=h_index, course=course)
            # expertList.append(expert)
            try:
                expert.save()
            except:
                print name
                # print university
                # print department
                # print tag
                # print link
                # print h_index
                # print course

    # Expert.objects.bulk_create(expertList)
    print('expert Done!')


def courseDump():
    f = xlrd.open_workbook('data/Courses.xlsx')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    courseList = []

    # row = table.row_values(1)
    # title = row[1]
    # university = row[2]
    # description = row[3]
    # publishDate = datetime.datetime.now()
    # link = row[4]
    # picture = row[5]
    # language = 1
    # if row[7] == u'英语':
    #     language = 2
    # rank = float(row[9])
    # popularity = float(row[10])
    # courseDate = datetime.datetime.strptime(datestr, "%Y/%m/%d")

    # print title
    # print university
    # print description
    # print link
    # print picture
    # timetuple = xldate_as_tuple(row[6], 0)
    # datestr = str(timetuple[0]) + '-' + str(timetuple[1]) + '-' + str(timetuple[2])
    # courseDate = datetime.datetime.now().strptime(datestr,"%Y-%m-%d")
    # print courseDate
    # print language
    # print rank
    # print popularity
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            title = row[1]
            university = row[2]
            description = row[3]
            publishDate = datetime.datetime.now()
            link = row[4]
            picture = row[5]
            language = 1
            if row[7] == u'英语':
                language = 2
            rank = float(row[9])
            popularity = float(row[10])

            try:
                timetuple = xldate_as_tuple(row[6], 0)
                datestr = str(timetuple[0]) + '-' + str(timetuple[1]) + '-' + str(timetuple[2])
                courseDate = datetime.datetime.now().strptime(datestr, "%Y-%m-%d")
                course = Course(title=title, university=university, description=description,
                                link=link, publishDate=publishDate, picture=picture,
                                language=language, rank=rank, popularity=popularity,
                                courseDate=courseDate
                                )
            except:
                course = Course(title=title, university=university, description=description,
                                link=link, publishDate=publishDate, picture=picture,
                                language=language, rank=rank, popularity=popularity
                                )
            courseList.append(course)

    Course.objects.bulk_create(courseList)
    print('course done')


def UserDump():
    f = xlrd.open_workbook('data/User.xlsx')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    userList = []

    # row = table.row_values(1)
    # username = row[1]
    # password = 'jingyishe123'
    # mail = row[2]
    # isActive = True
    # # timetuple = xldate_as_tuple(row[5], 0)
    # # datestr = str(timetuple[0]) + '-' + str(timetuple[1]) + '-' + str(timetuple[2])
    # date = datetime.datetime.now().strptime(row[5], "%Y-%m-%d %H:%M:%S")

    # print username,password,mail,date

    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            username = row[1]
            password = 'jingyishe123'
            mail = row[2]
            isActive = True
            date = datetime.datetime.now().strptime(row[5], "%Y-%m-%d %H:%M:%S")
            tag = row[11]
            user = User(username=username, password=password, mail=mail,
                        isActive=isActive, date=date, tag=tag)
            userList.append(user)

    User.objects.bulk_create(userList)
    print('user done')


def userModify():
    f = xlrd.open_workbook('data/User.xlsx')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            username = row[1]
            date = datetime.datetime.now().strptime(row[5], "%Y-%m-%d %H:%M:%S")
            user = User.objects.get(username=username)
            user.date = date
            user.save()

    print('usermodify done!')


def questionDump():
    f = xlrd.open_workbook('data/Qlist.xlsx')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            title = row[3]
            description = row[4]
            keyword = row[5]
            username = row[2]
            if row[7] == u'公开':
                isPublic = True
            else:
                isPublic = False
            date = datetime.datetime.now().strptime(row[1], "%Y-%m-%d %H:%M:%S")
            user = User.objects.get(username=username)
            if not user:
                user = User.objects.get(id=1)
            question = Question(title=title, description=description,
                                keyword=keyword, isPublic=isPublic,
                                questioner=user, publishDate=date)
            question.save()
    print ('question done!')


def answerDump():
    f = xlrd.open_workbook('data/Alist.xlsx')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    answerList = []
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        if row:
            content = row[4]
            question = Question.objects.get(id=row[1])
            answerer = User.objects.get(username=row[3])
            if row[6] == u'公开':
                isPublic = True
            else:
                isPublic = False
            answer = Answer(content=content, question=question, answerer=answerer,
                            isPublic=isPublic)
            answerList.append(answer)

    Answer.objects.bulk_create(answerList)
    print('answers done!')


def answerModify():
    f = xlrd.open_workbook('data/Alist.xlsx')
    table = f.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    answerCount = 1
    questionId = 1
    for rownum in range(2, nrows):
        row = table.row_values(rownum)
        if row:
            if row[1] == questionId:
                answerCount += 1
            else:
                question = Question.objects.get(id=questionId)
                question.answerNum = answerCount
                print questionId,answerCount
                question.save()
                answerCount = 1
                questionId = row[1]

    question = Question.objects.get(id=questionId)
    question.answerNum = answerCount
    question.save()
    print ('answer num done!')


if __name__ == "__main__":
    caseDump()
    expertDump()
    courseDump()
    UserDump()
    userModify()
    questionDump()
    answerDump()
    answerModify()
    print('Done!')
