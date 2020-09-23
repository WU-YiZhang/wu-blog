#-*- codeing = utf-8 -*-

'''
@Time : 2020-09-22 20:19
@Author : 吴艺长
@File: url.py
@Software: PyCharm
@python：3.6.8
'''
from django.conf.urls import url
# from django.urls import path
from users.views import RegisterView, LogInView

urlpatterns = [

    url(r"register/", RegisterView.as_view()),
    url(r"Login/", LogInView.as_view())
]