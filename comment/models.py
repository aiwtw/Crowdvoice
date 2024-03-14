from django.db import models
from django.db import models
from django.utils import timezone

from voice.models import User,Voicefile
from voice_share.models import Article


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )
    likes = models.PositiveIntegerField("喜欢",default=0,editable=False)
    content = models.TextField()
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.content[:20]

class CommentLike(models.Model):

    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    comment = models.ForeignKey(Comment,null=True,on_delete=models.SET_NULL)
    class Meta:
        verbose_name_plural = 'user'



class VoiceLike(models.Model):

    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    voice = models.ForeignKey(Voicefile,null=True,on_delete=models.SET_NULL)
    class Meta:
        verbose_name_plural = 'user'


class VoiceSharedLike(models.Model):

    user = models.ForeignKey(User,null=True,on_delete=models.SET_NULL)
    article = models.ForeignKey(Article,null=True,on_delete=models.SET_NULL)
    class Meta:
        verbose_name_plural = 'user'