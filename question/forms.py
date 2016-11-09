# -*- coding: utf-8 -*-
__author__ = 'apple'
from django import forms

from models import User

CHOICES_FOR_ANSWER = (('1', u'公开'), ('2', u'仅提问者可见'))
CHOICES_FOR_QUESTION = (('1', u'公开'), ('2', u'仅注册用户可见'))
CHOICES_FOR_LANGUAGE = (('1', u'中文'), ('2', u'英文'))
CHOICES_FOR_TIME = (('1', u'今天'), ('2', u'过去7天'), ('3', u'未来7天'))
CHOICES_FOR_ORDER = (('1', u'最新发布'), ('2', u'开课时间'), ('3', u'热度'))
CHOICES_FOR_MESSAGE = (('1', u'公开'), ('2', u'仅Ta可见'))
CHOICES_FOR_UPDATE = (('1', u'待解决'), ('2', u'已解决'))
CHOICES_FOR_CASE = (
    ('0', u'--请选择所属类别--'), ('统计学', u'统计学'), ('计算机科学', u'计算机科学'), ('人工智能', u'人工智能'), ('数据科学', u'数据科学'),
    ('机器人学', u'机器人学'),
    ('云计算', u'云计算'),
    ('智能信息系统', u'智能信息系统'), ('生物统计', u'生物统计'), ('机器学习', u'机器学习'))


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
    # isPublic = forms.ChoiceField(choices=CHOICES_FOR_MESSAGE, widget=forms.RadioSelect, initial='1')


class GlobalSearchForm(forms.Form):
    keyword = forms.CharField(required=False,
                              widget=forms.TextInput(
                                  attrs={'style': 'width:50;height:50;font-size:22px', 'size': '35'}))


class CourseSearchForm(forms.Form):
    keyword = forms.CharField(required=False,
                              widget=forms.TextInput(
                                  attrs={'style': 'width: 60; height: 40; font-size: 18px', 'size': '60',
                                         'placeholder': '请输入关键词'}))
    language = forms.ChoiceField(choices=CHOICES_FOR_LANGUAGE, widget=forms.RadioSelect,required=False)
    time = forms.ChoiceField(choices=CHOICES_FOR_TIME, widget=forms.RadioSelect,required=False)
    order = forms.ChoiceField(choices=CHOICES_FOR_ORDER, widget=forms.RadioSelect,required=False)


class MessageAnswerForm(forms.Form):
    answer = forms.CharField(widget=forms.Textarea(attrs={'cols': '148', 'rows': '10'}))


class CaseForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'size': '60', 'maxlength': '100', 'style': 'width:60; height:40; font-size:18px'}))
    category = forms.ChoiceField(choices=CHOICES_FOR_CASE, initial='0',
                                 widget=forms.Select(attrs={'onChange': 'CaseCategory()'}))
    # direction = forms.ChoiceField(choices=(('0', u'--请选择所在研究方向--'),))
    questionDescription = forms.CharField(widget=forms.Textarea(attrs={'cols': '135', 'rows': '8'}))
    attachedDescription = forms.FileField(required=False, widget=forms.ClearableFileInput())
    dataDescription = forms.CharField(widget=forms.Textarea(attrs={'cols': '135', 'rows': '5'}))
    keyword = forms.CharField(widget=forms.TextInput(
        attrs={'size': '90', 'maxlength': '100', 'style': 'width:60; height:40; font-size:16px'}))
    solution = forms.CharField(widget=forms.Textarea(attrs={'cols': '135', 'rows': '10'}))
    attachedSolution = forms.FileField(required=False, widget=forms.ClearableFileInput())
    source = forms.CharField(widget=forms.Textarea(attrs={'cols': '135', 'rows': '5'}), required=False)
    reference = forms.CharField(widget=forms.Textarea(attrs={'cols': '135', 'rows': '5'}), required=False)
