import re

from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect

# Create your views here.


# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection


from users.models import User


class RegisterView(View):
    def get(self,request):
        return render(request, 'register.html')

    def post(self, request):

        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password_2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')

        # 判断参数齐全
        if not all([mobile,password,password_2,smscode]):
            return HttpResponseBadRequest('缺少必要参数')

        # 判断参数是否合法
        # 判断手机号码格式
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest("手机号码格式不对")

        # 判断密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest("请输入8~20位的密码")

        # 判断两次密码是否一致
        if password != password_2:
            return HttpResponseBadRequest("两次密码输入不一致")

        # 验证短信验证码
        redis_conn = get_redis_connection("default")
        sms_code_server = redis_conn.get("sms:%s" % mobile)

        # 检验短信验证码是否过期
        if sms_code_server is None:
            return HttpResponseBadRequest("短信验证码过期")

        # 保存注册数据
        try:
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)

        except DatabaseError:
            return HttpResponseBadRequest("注册失败")

        # 状态保持
        login(request, user)

        # 重定向首页
        response = redirect(reverse('home:index'))

        # 设置cookie
        # 登录状态，会话结束自动过期
        response.set_cookie('is_login', True)

        # 设置用户名有效期一个月
        response.set_cookie('username', user.username, max_age=30*24*3600)

        return response


class LogInView(View):

    def get(self, request):
        return render(request, 'login.html')