from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 300  # Default page size; adjust as needed
    page_size_query_param = "page_size"  # Allow the client to specify page size

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": total_pages,
                "current_page": self.page.number,
                "results": data,
            }
        )
