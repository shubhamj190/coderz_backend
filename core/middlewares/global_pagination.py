import math
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'item_per_page'
    max_page_size = 100

    def get_paginated_response(self, data):
        total = self.page.paginator.count
        items_per_page = self.get_page_size(self.request) or self.page_size
        total_pages = math.ceil(total / items_per_page) if items_per_page else 1
        
        next_page = self.page.next_page_number() if self.page.has_next() else None
        previous_page = self.page.previous_page_number() if self.page.has_previous() else None
        
        return Response({
            'count': total,                 # Total number of items
            'total_pages': total_pages,     # Total number of pages
            'items_per_page': items_per_page,
            'next': next_page,              # Next page number (or null if no next page)
            'previous': previous_page,      # Previous page number (or null if no previous page)
            'results': data
        })