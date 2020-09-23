from django.shortcuts import render

# Create your views here.


# Create your views here.
from django.http import HttpResponse
from django.views import View


class RegisterView(View):
    def get(self, request):

        return HttpResponse("注册")


class LogInView(View):

    def post(self, request):

        return HttpResponse("登录")