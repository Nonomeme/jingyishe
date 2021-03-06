"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from question import urls as question_urls
from question import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^index/$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^forgetPassword/$', views.forgetPwd, name='forgetPwd'),
    url(r'^updatePassword/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', views.updatePwd, name='updatePwd'),
    url(r'^question/', include(question_urls)),
    url(r'^aboutus/$', views.aboutus, name='aboutus'),
    url(r'^users/(?P<user_id>[0-9]+)/$', views.userInfo, name='userInfo'),
    url(r'^users/(?P<user_id>[0-9]+)/tag/$', views.userTag, name='userTag'),
    url(r'^users/(?P<publisher_id>[0-9]+)/follow/$', views.followUser, name='followUser'),
    url(r'^users/(?P<user_id>[0-9]+)/message/$', views.leaveMessage, name='leaveMessage'),
    url(r'^users/(?P<user_id>[0-9]+)/message/(?P<message_id>[0-9]+)/$', views.answerMessage, name='answerMessage'),
    url(r'^users/(?P<user_id>[0-9]+)/questions/$', views.myquestions, name='myquestions'),
    url(r'^users/(?P<user_id>[0-9]+)/answers/$', views.myanswers, name='myanswers'),
    url(r'^users/(?P<user_id>[0-9]+)/cases/$', views.mycases, name='mycases'),
    url(r'^users/(?P<user_id>[0-9]+)/sharings/$', views.mysharings, name='mysharings'),
    url(r'^consultion/$', views.consultion, name='consultion'),
    url(r'^expert/$', views.expert, name='expert'),
    url(r'^case/$', views.case, name='case'),
    url(r'^case/(?P<case_id>[0-9]+)/attachedFile/$', views.downloadCase, name='downloadCase'),
    url(r'^case/(?P<case_id>[0-9]+)/attachedSolution/$', views.downloadSolution, name='downloadSolution'),
    url(r'^case/(?P<case_id>[0-9]+)/$', views.caseDetail, name='caseDetail'),
    url(r'^case/(?P<case_id>[0-9]+)/follow/$', views.caseFollow, name='caseFollow'),
    url(r'^addcase/$', views.addCase, name='addCase'),
    url(r'^search/$', views.search, name='search'),
    url(r'^answer/(?P<answer_id>[0-9]+)/agree/$', views.grade, name='grade'),
    url(r'^courses/$', views.courses, name='courses'),
    url(r'^users/activate/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', views.activateUser, name='activateUser'),
    # url(r'^captcha/', include('captcha.urls')),
]
