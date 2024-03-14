from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from voice.models import User

class Article(models.Model):
    user = models.ForeignKey(to=User, related_name='article', on_delete=models.SET,
                             blank=True, null=True)
    # 标题
    title = models.CharField(max_length=100)
    # 正文
    text = models.TextField()
    # 创建时间
    created = models.DateTimeField(default=timezone.now)
    # 点赞数
    likes = models.PositiveIntegerField("喜欢", default=0, editable=False)

    shared_voice_url = models.CharField(max_length=256, blank=True, null=True)


    def __str__(self):
        return self.title