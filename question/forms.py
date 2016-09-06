# -*- coding: utf-8 -*-
__author__ = 'apple'
from django import forms

from models import User

CHOICES_FOR_ANSWER = (('1', u'公开'), ('2', u'仅提问者可见'))
CHOICES_FOR_QUESTION = (('1', u'公开'), ('2', u'仅注册用户可见'))
CHOICES_FOR_MESSAGE = (('1', u'公开'), ('2', u'仅Ta可见'))
CHOICES_FOR_UPDATE = (('1', u'待解决'), ('2', u'已解决'))


class AnswerForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': '输入回答内容', 'cols': '161', 'rows': '20'}))
    isPublic = forms.ChoiceField(choices=CHOICES_FOR_ANSWER, widget=forms.RadioSelect, initial='1')
    attachedFile = forms.FileField(required=False)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'mail')
        widgets = {
            'password': forms.PasswordInput(attrs={'style': 'width: 60; height: 40; font-size: 16px', 'size': '32'}),
            'username': forms.TextInput(attrs={'style': 'width: 60; height: 40; font-size: 16px', 'size': '32'}),
            'mail': forms.TextInput(attrs={'style': 'width: 60; height: 40; font-size: 16px', 'size': '32'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'style': 'width: 60; height: 40; font-size: 16px', 'size': '32'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'style': 'width: 60; height: 40; font-size: 16px', 'size': '32'}))


class QuestionForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '66', 'maxlength': '100'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': '80', 'rows': '15'}))
    keyword = forms.CharField(widget=forms.TextInput(attrs={'size': '72', 'maxlength': '100'}))
    attachedFile = forms.FileField(required=False, widget=forms.ClearableFileInput())
    isPublic = forms.ChoiceField(choices=CHOICES_FOR_QUESTION, widget=forms.RadioSelect, initial='1')
    # isSolved = forms.ChoiceField(choices=CHOICES_FOR_UPDATE, widget=forms.RadioSelect, initial='1')
    attachedDescription = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': '140', 'rows': '10'}))


class QuestionForm2(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'size': '60', 'maxlength': '100', 'style': 'width:60; height:40; font-size:18px'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': '140', 'rows': '15'}))
    keyword = forms.CharField(widget=forms.TextInput(
        attrs={'size': '55', 'maxlength': '100', 'style': 'width:60; height:40; font-size:16px'}))
    attachedFile = forms.FileField(required=False, widget=forms.ClearableFileInput())
    isPublic = forms.ChoiceField(choices=CHOICES_FOR_QUESTION, widget=forms.RadioSelect, initial='1')
    # isSolved = forms.ChoiceField(choices=CHOICES_FOR_UPDATE, widget=forms.RadioSelect, initial='1')
    attachedDescription = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols': '140', 'rows': '10'}))


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False,
                              widget=forms.TextInput(
                                  attrs={'style': 'width: 60; height: 40; font-size: 18px', 'size': '60',
                                         'placeholder': '请输入关键词'}))
    # hasPic = forms.BooleanField(required=False)
    isToday = forms.BooleanField(required=False)
    isHot = forms.BooleanField(required=False)


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': '148', 'rows': '8'}))
    isPublic = forms.ChoiceField(choices=CHOICES_FOR_MESSAGE, widget=forms.RadioSelect, initial='1')


class GlobalSearchForm(forms.Form):
    keyword = forms.CharField(required=False,
                              widget=forms.TextInput(
                                  attrs={'style': 'width:50;height:50;font-size:22px', 'size': '35'}))


class MessageAnswerForm(forms.Form):
    answer = forms.CharField(widget=forms.Textarea(attrs={'cols': '148', 'rows': '10'}))
