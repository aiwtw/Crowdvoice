from rest_framework import serializers

from voice_share.models import Article
from comment.serializers import CommentSerializer


class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'created',
            'likes',
        ]


class ArticleDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id',
            'user',
            'title',
            'text',
            'created',
            'likes',
            'shared_voice_url',
            'comments',
        ]

