from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from Blog.libs.captcha.captcha import captcha


class ImageCodeView(View):
    def get(self,request):
        # 获取前端传递的uuid
        uuid = request.GET.get('uuid')

        # 判断参数是否为None

        if uuid is None:
            return HttpResponseBadRequest('请求参数错误')

        # 获取验证码内容个图片二进制数据
        text, image = captcha.generate_captcha()

        # 将图片验证码内容保存到redis中，并设置过期时间
        redis_conn = get_redis_connection('default')
        redis_conn.setex('img:%s' % uuid, 300, text)
        return HttpResponse(image, content_type='image/jpeg')
