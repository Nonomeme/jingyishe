# coding=utf-8
from __future__ import unicode_literals

from django.db import models


# from django.contrib.auth.models import User
# from django.contrib.auth.models import AbstractUser


# Create your models here.
# class NewUser(AbstractUser):
# mail = models.EmailField(blank=True)
#     tag = models.CharField(max_length=256, blank=True)
#     followingQuestion = models.ManyToManyField('question.Question', blank=True)
#     followingPerson = models.ManyToManyField("self", blank=True)
#
#     def __unicode__(self):
#         return self.username

class User(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    mail = models.EmailField()
    tag = models.CharField(max_length=256, blank=True)
    isActive = models.BooleanField(default=False)
    followingQuestion = models.ManyToManyField('question.Question', blank=True, through='QuestionFollow',
                                               through_fields=('questionFollower', 'followingQuestion'))
    followingPerson = models.ManyToManyField("self", blank=True, symmetrical=False, through='PersonFollow',
                                             through_fields=('userFollower', 'followingPerson'))
    followingCase = models.ManyToManyField('question.Case', blank=True, through='CaseFollow')

    gradeAnswer = models.ManyToManyField('question.Answer', blank=True)

    date = models.DateTimeField(auto_now_add=True)


    def __unicode__(self):
        return self.username


class Question(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField()
    keyword = models.CharField(max_length=256)
    isPublic = models.BooleanField(default=True)
    publishDate = models.DateTimeField(auto_now_add=True)
    attachedFile = models.FileField(blank=True,upload_to='question')
    isSolved = models.BooleanField(default=False)
    questioner = models.ForeignKey(User)
    answerNum = models.IntegerField(default=0)
    attachedDescription = models.TextField(default='')

    def __unicode__(self):
        return self.title


class Answer(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    content = models.TextField()
    question = models.ForeignKey(Question)
    answerer = models.ForeignKey(User)
    publishDate = models.DateTimeField(auto_now_add=True)
    attachedFile = models.FileField(blank=True,upload_to='answer')
    # attachedFile = models.FileField(blank=True, upload_to='./upload/')
    isPublic = models.BooleanField()
    grade = models.IntegerField(default=0)

    def __unicode__(self):
        return self.question.title


class Message(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    message = models.TextField()
    commenter = models.OneToOneField(User)
    receiver = models.OneToOneField(User, related_name='receiver')
    isPublic = models.BooleanField()
    publishDate = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message


class MessageAnswer(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    answer = models.TextField()
    message = models.ForeignKey(Message)
    publishDate = models.DateTimeField(auto_now_add=True)


class Expert(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=20)
    university = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    tag = models.CharField(max_length=256)
    link = models.CharField(max_length=256)
    h_index = models.IntegerField(default=0)
    course = models.CharField(max_length=256,blank=True)

    def __unicode__(self):
        return self.name


class PersonFollow(models.Model):
    userFollower = models.ForeignKey(User, related_name='userFollower', on_delete=models.CASCADE)
    followingPerson = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class QuestionFollow(models.Model):
    questionFollower = models.ForeignKey(User, on_delete=models.CASCADE)
    followingQuestion = models.ForeignKey(Question, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class Case(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=100)
    questionDescription = models.TextField()
    dataDescription = models.TextField()
    solution = models.TextField()
    keyword = models.CharField(max_length=256)
    source = models.CharField(max_length=256, blank=True)
    reference = models.TextField(blank=True)
    caseType = models.CharField(max_length=20)
    # domain = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)
    attachedDescription = models.FileField(blank=True,upload_to='case')
    attachedSolution = models.FileField(blank=True,upload_to='caseSolution')
    uploader = models.ForeignKey(User)

    def __unicode__(self):
        return self.title


class CaseFollow(models.Model):
    caseFollower = models.ForeignKey(User, on_delete=models.CASCADE)
    followingCase = models.ForeignKey(Case, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)


class Course(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=256)
    university = models.CharField(max_length=256)
    description = models.TextField()
    publishDate = models.DateTimeField(auto_now_add=True)
    language = models.IntegerField(default=1)   #1代表中文 2代表英文 3代表中/英
    courseDate = models.DateTimeField(null=True)
    rank = models.FloatField(default=0)
    popularity = models.FloatField(default=0)
    link = models.CharField(max_length=256)
    picture = models.ImageField(blank=True)
