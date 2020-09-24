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
from users.views import RegisterView, LogInView, LogoutView, ForgetPasswordView

urlpatterns = [
    # 注册路由
    url(r"register/", RegisterView.as_view(), name="register"),

    # 登录路由
    url(r"login/", LogInView.as_view(), name='login'),

    # 退出登录路由
    url(r'logout/', LogoutView.as_view(), name='logout'),

    # 忘记密码页面路由
    url(r'forgetpassword/', ForgetPasswordView.as_view(), name='forgetpassword'),

]