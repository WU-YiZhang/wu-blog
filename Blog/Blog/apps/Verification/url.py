#-*- codeing = utf-8 -*-

'''
@Time : 2020-09-22 20:19
@Author : 吴艺长
@File: url.py
@Software: PyCharm
@python：3.6.8
'''
from django.conf.urls import url
from Verification.views import ImageCodeView

urlpatterns = [

    url(r"imagecode/", ImageCodeView.as_view()),
]