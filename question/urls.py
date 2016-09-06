__author__ = 'apple'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<question_id>[0-9]+)/attachedFile/$', views.download, name='download'),
    url(r'^(?P<question_id>[0-9]+)/answer/$', views.answer, name='answer'),
    url(r'^$', views.question, name='question'),
    url(r'^(?P<question_id>[0-9]+)/follow/$', views.followQuestion, name='followQuestion'),
    url(r'^(?P<question_id>[0-9]+)/(?P<publisher_id>[0-9]+)/follow/$', views.followPerson, name='followPerson'),
    url(r'^latest/$', views.latestQuestion, name='latestQuestion'),
    url(r'^latest/(?P<type>[0-9])/$', views.latestQuestion, name='latestQuestion'),
    url(r'^answer/(?P<answer_id>[0-9]+)/attachedFile/$', views.downloadAnswer, name='downloadAnswer'),
    url(r'^(?P<question_id>[0-9]+)/relatedQuestions/$', views.relatedQuestions, name='relatedQuestions'),
    url(r'^(?P<question_id>[0-9]+)/update/$', views.updateQuestion, name='updateQuestion'),

]
