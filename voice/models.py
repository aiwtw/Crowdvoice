# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import datetime
import os
from tabnanny import verbose

from django.contrib.auth.models import AbstractUser
import django.utils.timezone as timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from TTS1 import settings
# Create your models here.

class User(AbstractUser):
    usertype = models.SmallIntegerField(choices=((1, '普通用户'), (2, '管理员')), default=2, verbose_name='用户类型')
    phone = models.CharField(verbose_name="电话",max_length=13)
    email = models.CharField(verbose_name="邮箱",max_length=32)
    sexy = models.BooleanField(default=False)
    VIP = models.BooleanField(default=False)
    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'

class Voicefile(models.Model):
    url = models.CharField(max_length=256, verbose_name="音频地址")
    name = models.CharField(max_length=32, verbose_name="音频名称", null=True)
    user = models.ForeignKey(to=User, verbose_name="音频", related_name='voice', on_delete=models.SET,
                              blank=True, null=True)
    likes = models.PositiveIntegerField("喜欢",default=0,editable=False)
    class Meta:
        db_table = 'Voicefile'

class UserSound(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sound_file = models.FileField(upload_to='./')#这里更目录指的是media
    name = models.TextField(default='None')
    description = models.TextField(default='None')##用户可以备注
    time = models.TextField(default='None')
    path = models.TextField(default='None')
    class Meta:
        db_table = 'Usersound'

@receiver(pre_delete, sender=UserSound)
def file_model_pre_delete(sender, instance, **kwargs):
    # 删除文件
    if instance.sound_file:
        file_path = os.path.join(settings.MEDIA_ROOT, instance.sound_file.name)
        if os.path.exists(file_path):
            os.remove(file_path)