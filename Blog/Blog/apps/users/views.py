import re

from django.contrib.auth import login, authenticate, logout

from django.db import DatabaseError
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from settings.dev import QINIU_DOMAIN
from users.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from libs.qiniuyun.tupian import upload_file



"""注册接口"""
class RegisterView(View):
    def get(self, request):
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


"""登录接口"""
class LogInView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self,request):
        mobile = request.POST.get("mobile")

        password = request.POST.get("password")

        remember = request.POST.get("remember")

        # 检验参数齐全
        if not all([mobile, password]):
            return HttpResponseBadRequest("缺少必要参数")

        # 检验手机号码
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest("请输入正确手机号码")

        # 检验密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest("请输入8~20位的密码")

        # 认证登录用户
        # 认证字段已经在User模型中的UESRNAME——FIELD = 'mobile'修改
        user = authenticate(mobile=mobile, password=password)

        try:
            User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号码查询不到用户，则注册新用户
            return redirect(reverse("users:register"))

        if user is None:
            return HttpResponseBadRequest("用户名或密码错误")

        # 实现转态保持
        login(request, user)

        next= request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            # 响应登录结果
            response = redirect(reverse('home:index'))

        # 设置状态保存周期
        # 判断是否记住密码
        if remember != "no":
            # 没有记住密码：浏览器结束会话就过期
            request.session.set_expiry(0)

            # 设置cookie
            response.set_cookie('is_login', True)
            response.set_cookie('username', user.username, max_age=30 * 24 * 3600)

        else:
            # 记住密码： None表示两周后过期
            request.session.set_expiry(None)
            response.set_cookie("is_login", True, max_age=14*24*360)
            response.set_cookie("username", user.username, max_age=30*24*3600)

        return response


"""退出登录接口"""
class LogoutView(View):
    def get(self,request):
        # 清除session
        logout(request)

        # 退出登录，重定向到首页页面
        response = redirect(reverse('home:index'))

        # 退出时清除cookie中的登录状态
        response.delete_cookie('is_login')

        return response


"""忘记密码接口"""
class ForgetPasswordView(View):
    # 重定向忘记密码页面
    def get(self, request):
        return render(request, 'forget_password.html')

    def post(self, request):
        mobile = request.POST.get("mobile")

        password = request.POST.get('password')

        password2 = request.POST.get('password2')

        sms_code = request.POST.get("sms_code")

        if not all([mobile, password, password2, sms_code]):
            return HttpResponseBadRequest('缺少必要参数')

        # 判断参数是否合法
        # 判断手机号码格式
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest("手机号码格式不对")

        # 判断密码格式
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest("请输入8~20位的密码")

        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseBadRequest("两次密码输入不一致")

        # 验证短信验证码
        redis_conn = get_redis_connection("default")
        sms_code_server = redis_conn.get("sms:%s" % mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest('验证码过期')

        if sms_code != sms_code_server.decode():
            return HttpResponseBadRequest("短信验证码错误")

        # 根据手机号码查询
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 手机号码查询不到用户，则注册新用户
            try:
                User.objects.create_user(username=mobile,mobile=mobile,password=password)
            except Exception:
                return HttpResponseBadRequest("修改失败，稍后再试")

        else:
            # 修改密码
            user.set_password(password)
            # 保存
            user.save()
        response = redirect(reverse("users:login"))
        return response


"""用户中心接口 """
class UserCenterView(LoginRequiredMixin, View):
    # 页面展示
    def get(self, request):
        # 获取用户信息
        user = request.user
        if user.avatar:
            avatar = user.avatar.url
            file_url = QINIU_DOMAIN + avatar
            print(file_url)

        else:
            file_url = None
        context = {
            "username": user.username,
            "mobile": user.mobile,
            "avatar": file_url,
            "user_desc": user.user_desc
        }

        return render(request, 'center.html', context=context)

    # 用户中心修改
    def post(self, request):
        # 接受数据
        user = request.user
        avatar = request.FILES.get("avatar")
        username = request.POST.get("username", user.username)
        user_desc = request.POST.get('desc', user.user_desc)

        file_url = upload_file(avatar)



        # 修改数据
        try:
            user.username = username
            user.user_desc = user_desc
            user.avatar = file_url
            user.save()
        except Exception as e:
            return HttpResponseBadRequest("更新数据失败，请稍后再试")

        # 返回响应，刷新页面
        response = redirect(reverse('users:center'))

        # 更新cookie信息
        response.set_cookie('username', user.username, max_age=30*24*3600)
        return response




















