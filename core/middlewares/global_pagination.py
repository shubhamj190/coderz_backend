from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size =50                   # Default page size
    page_size_query_param = 'page'
    max_page_size = 100