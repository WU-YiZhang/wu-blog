from random import randint

from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from Blog.libs.captcha.captcha import captcha
import logging

from Blog.libs.yuntongxun.sms import CCP

logger = logging.getLogger('django')


class ImageCodeView(View):
    def get(self, request):
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


class SMSCodeView(View):
    def get(self, request):
        # 接受参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        mobile=request.GET.get('mobile')

        # 检验参数是否为空
        if not all([image_code_client, uuid, mobile]):
            return JsonResponse({'code': 400, "errmsg": "缺少必要参数"})

        # 创建连接redis的对象
        redis_conn = get_redis_connection('default')

        # 提取图形验证码
        image_code_server = redis_conn.get('img:%s' % uuid)

        # 判断图形验证码是否过期
        if image_code_server is None:

            return JsonResponse({'code': 400, "errmsg": "图形验证码失效"})

        # 删除图形验证码
        try:
            redis_conn.delete('img:%s' % uuid)

        except Exception as e:
            logger.error(e)

        # 对比图形验证码
        image_code_server = image_code_server.decode()  # bytes转字符串

        if image_code_client.lower() != image_code_server.lower():  # 装换小写比较（因为有的人输入不同大大小写）
            return JsonResponse({'code': 400, "errmsg": "图形验证码错误"})

        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)

        # 将短信验证码输出到控制台，调试用
        logger.info(sms_code)

        # 保存短信到redis中，设置有效期
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)

        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)

        # 返回响应结果
        return JsonResponse({"code": "200", "errmsg": "ok"})