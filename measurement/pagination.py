from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50


class PostPageNumberPagination(PageNumberPagination):
    page_size = 50
