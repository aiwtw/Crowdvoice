from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

from rest_framework import viewsets

from comment.models import Comment, CommentLike, VoiceSharedLike
from comment.serializers import CommentSerializer
from comment.permissions import IsOwnerOrReadOnly
from voice_share.models import Article


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class IncreaseCommentLikeView(APIView):
    def post(self, request, pk):
        user = request.user
        comment = Comment.objects.get(pk=pk)
        try:
            CommentLike.objects.get(user=user, comment=comment)
        except CommentLike.DoesNotExist:
            comment_like = CommentLike(user=user, comment=comment)
            comment.likes += 1
            comment.save()
            comment_like.save()
            return Response({
                'status': 201,
                'msg': '点赞成功',
            })
        else:
            return Response({
                'status': 201,
                'msg': '这条评论已经被用户点赞过了',
            })

    def delete(self, request, pk):
        user = request.user
        comment = Comment.objects.get(pk=pk)
        try:
            CommentLike.objects.get(user=user, comment=comment)
        except CommentLike.DoesNotExist:
            return Response({
                'status': 201,
                'msg': '没有相关点赞记录',
            })
        else:
            comment_like = CommentLike.objects.get(user=user, comment=comment)
            comment.likes -= 1
            comment.save()
            comment_like.delete()
            return Response({
                'status': 201,
                'msg': '取消赞成功',
            })

class IncreaseVoiceSharedLikeView(APIView):
    def post(self, request, pk):
        user = request.user
        article = Article.objects.get(pk=pk)
        try:
            VoiceSharedLike.objects.get(user=user, article=article)
        except VoiceSharedLike.DoesNotExist:
            article_like = VoiceSharedLike(user=user, article=article)
            article.likes += 1
            article.save()
            article_like.save()
            return Response({
                'status': 201,
                'msg': '点赞成功',
            })
        else:
            return Response({
                'status': 201,
                'msg': '这个主题文章已经被用户点赞过了',
            })

    def delete(self, request, pk):
        user = request.user
        article = Article.objects.get(pk=pk)
        try:
            VoiceSharedLike.objects.get(user=user, article=article)
        except VoiceSharedLike.DoesNotExist:
            return Response({
                'status': 201,
                'msg': '没有相关点赞记录',
            })
        else:
            article_like = VoiceSharedLike.objects.get(user=user, article=article)
            article.likes -= 1
            article.save()
            article_like.delete()
            return Response({
                'status': 201,
                'msg': '取消赞成功',
            })
