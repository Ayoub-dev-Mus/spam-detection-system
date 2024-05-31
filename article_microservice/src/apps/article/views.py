import json
from sqlite3 import DatabaseError
from django.http import JsonResponse
from rest_framework.decorators import api_view
from utils.kafka import KafkaUtils
from .serializers import ArticleSerializer, CreateArticleSerializer
from .models import Article
from rest_framework.response import Response
from rest_framework import status
from utils.jwt_middleware import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import authentication_classes

@swagger_auto_schema(
    method='get',
    responses={200: ArticleSerializer(many=True)},
    authentication_classes=[JWTAuthentication]
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def get_all_articles(request):

    articles = Article.objects.all()
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=CreateArticleSerializer,
    responses={201: ArticleSerializer(), 400: 'Bad Request'},
    authentication_classes=[JWTAuthentication]

)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def create_article(request):
    try:
        user_id = request.user
        request.data['authorId'] = user_id
        serializer = CreateArticleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article = serializer.save()


        message_data = {
            'article_id': article.id,
            'title': article.title,
            'content': article.content
        }


        kafka_utils = KafkaUtils()
        kafka_utils.produce_message(key=str(article.id), message=message_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'error': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
def update_article_status(request, article_id):
    try:
        is_spam = request.data.get('is_spam')
        if is_spam is None:
            return Response({"error": "is_spam field is required"}, status=400)
        try:
            article = Article.objects.get(id=article_id)
            article.is_spam = is_spam
            article.save()
            return Response({"message": "Article status updated successfully."}, status=200)
        except Article.DoesNotExist:
            return Response({"error": "Article not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON"}, status=400)



def update_article_in_db(article_id, is_spam):
    try:
        article = Article.objects.get(id=article_id)
        article.is_spam = is_spam
        article.save()
        return {"message": "Article status updated successfully."}
    except Article.DoesNotExist:
        return {"error": "Article not found.", "status": 404}
    except DatabaseError as e:
        return {"error": str(e), "status": 500}
