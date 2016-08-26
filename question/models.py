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
    followingQuestion = models.ManyToManyField('question.Question', blank=True, through='QuestionFollow',
                                               through_fields=('questionFollower', 'followingQuestion'))
    followingPerson = models.ManyToManyField("self", blank=True, symmetrical=False, through='PersonFollow',
                                             through_fields=('userFollower', 'followingPerson'))
    followingCase = models.ManyToManyField('question.Case', blank=True, through='CaseFollow')

    def __unicode__(self):
        return self.username


class Question(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField()
    keyword = models.CharField(max_length=256)
    isPublic = models.BooleanField(default=True)
    publishDate = models.DateTimeField(auto_now_add=True)
    attachedFile = models.FileField(blank=True)
    isSolved = models.BooleanField(default=False)
    questioner = models.ForeignKey(User)

    def __unicode__(self):
        return self.title


class Answer(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    content = models.TextField()
    question = models.ForeignKey(Question)
    answerer = models.ForeignKey(User)
    publishDate = models.DateTimeField(auto_now_add=True)
    attachedFile = models.FileField(blank=True, upload_to='./upload/')
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


class Expert(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=20)
    university = models.CharField(max_length=50)
    tag = models.CharField(max_length=200)
    link = models.CharField(max_length=200)

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
    source = models.CharField(max_length=256)
    reference = models.TextField()
    caseType = models.CharField(max_length=20)
    domain = models.CharField(max_length=20)

    def __unicode__(self):
        return self.title


class CaseFollow(models.Model):
    caseFollower = models.ForeignKey(User, on_delete=models.CASCADE)
    followingCase = models.ForeignKey(Case, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
