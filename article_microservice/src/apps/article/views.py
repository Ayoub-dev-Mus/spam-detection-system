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

        # Prepare message data for Kafka
        message_data = {
            'article_id': article.id,
            'title': article.title,
            'content': article.content
        }

        # Produce message to Kafka
        kafka_utils = KafkaUtils()
        kafka_utils.produce_message(key=str(article.id), message=message_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'error': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
