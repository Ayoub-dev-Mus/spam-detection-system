
from django.urls import path
from .views import create_article , get_all_articles

urlpatterns = [
    path("article/", create_article, name="get_all_articles"),
    path("article", get_all_articles, name="create_article"),
]