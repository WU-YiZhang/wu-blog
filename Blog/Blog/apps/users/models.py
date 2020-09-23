from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

# 导入
from django.db import models
from django.contrib.auth.models import AbstractUser


# 重写用户模型类, 继承自 AbstractUser
class User(AbstractUser):
    """自定义用户模型类"""

    # 额外增加 mobile 字段
    mobile = models.CharField(max_length=11, unique=True,blank=False, verbose_name='手机号')

    # 添加头像地址字段
    avatar = models.ImageField(blank=True, verbose_name='头像地址')

    # 添加简介字段
    user_desc = models.TextField(max_length=500, blank=True, verbose_name='简介')

    # 修改认证的字段
    USERNAME_FIELD = 'mobile'

    # 创建超级管理员时需要必须输入的字段
    REQUIRED_FIELDS = ['username', 'email']

    # 对当前表进行相关设置:
    class Meta:
        db_table = 'tb_users'           # 修改默认的表名
        verbose_name = '用户信息'          # Admin后台显示
        verbose_name_plural = verbose_name  # Admin后台显示

    # 在 str 魔法方法中, 返回
    def __str__(self):
        return self.mobile