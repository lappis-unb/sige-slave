from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination


class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50


class PostPageNumberPagination(PageNumberPagination):
    page_size = 50
