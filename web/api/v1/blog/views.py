from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin

from blog.models import Article
from blog.choices import ArticleStatus
from main.pagination import BasePageNumberPagination
from . import serializers

class ArticleListView(GenericAPIView):
    permission_classes = (AllowAny, )
    serializer_class = serializers.ArticleSerializer
    pagination_class = BasePageNumberPagination

    def get(self, request):
        queryset = Article.objects.filter(status=ArticleStatus.ACTIVE).select_related('category', 'author')
        page = self.paginate_queryset(queryset)
        serializer = serializers.ArticleSerializer(page, 
                                                many=True, context={'request': request
                                                                       })
        return self.get_paginated_response(serializer.data)