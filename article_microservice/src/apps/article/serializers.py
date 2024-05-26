from .models import Article
from rest_framework import serializers


class CreateArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'content', 'authorId', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'author')

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('title', 'content', 'authorId', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'author')