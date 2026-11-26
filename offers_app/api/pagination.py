from rest_framework.pagination import PageNumberPagination


class GetOffersPagination(PageNumberPagination):
    """
    Paginates the offer list and allows a custom page size via page_size.
    """
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 100
