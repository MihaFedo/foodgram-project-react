from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class CustomSetPagination(PageNumberPagination):
    page_size_query_param = 'limit'
