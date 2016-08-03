from __future__ import unicode_literals

import datetime
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class NewUser(AbstractUser):
    mail = models.EmailField(blank=True)
    tag = models.CharField(max_length=256,blank=True)
    followingQuestion = models.ManyToManyField('question.Question',blank=True)
    followingPerson = models.ManyToManyField("self",blank=True)

    def __str__(self):
        return self.username

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=256)
    description = models.TextField()
    keyword = models.CharField(max_length=256)
    isPublic = models.BooleanField()
    publishDate = models.DateTimeField(auto_now_add=True)
    attachedFile = models.FileField(blank=True)
    isSolved = models.BooleanField()
    questioner = models.ForeignKey(NewUser)

    def __str__(self):
        return self.title.encode('utf8')

class Answer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    content = models.TextField()
    question = models.ForeignKey(Question)
    answerer = models.ForeignKey(NewUser)
    isAnonym = models.BooleanField()
    publishDate = models.DateTimeField(auto_now_add=True)
    attachedFile = models.FileField(blank=True)
    isPublic = models.BooleanField()
    grade = models.IntegerField(default=0)

    def __str__(self):
        return self.question.title.encode('utf8')

