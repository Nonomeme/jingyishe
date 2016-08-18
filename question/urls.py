__author__ = 'apple'
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<question_id>[0-9]+)/comment/$', views.comment, name='comment'),
    url(r'^$', views.question, name='question'),
    url(r'^(?P<question_id>[0-9]+)/follow/$', views.followQuestion, name='followQuestion'),
    url(r'^(?P<question_id>[0-9]+)/(?P<publisher_id>[0-9]+)/follow/$', views.followPerson, name='followPerson'),
    url(r'^latest/',views.latestQuestion,name='latestQuestion')
]
