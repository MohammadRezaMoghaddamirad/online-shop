from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend


class ProductSearchFilter(BaseFilterBackend):
    """
    جست‌وجوی محصولات:
    - عبارت داخل نام یا توضیحات باشد (مثل قبل)، یا
    - نام محصول شبیه عبارت باشد (تحمل غلط املایی با pg_trgm).
    نتیجه‌ها بر اساس شباهت نام مرتب می‌شوند، مگر اینکه ?ordering داده شده باشد.
    """
    search_param = 'search'

    def filter_queryset(self, request, queryset, view):
        term = request.query_params.get(self.search_param, '').strip()
        if not term:
            return queryset

        queryset = queryset.annotate(
            search_rank=TrigramSimilarity('name', term)
        ).filter(
            Q(name__trigram_similar=term)
            | Q(name__icontains=term)
            | Q(description__icontains=term)
        )

        if 'ordering' not in request.query_params:
            queryset = queryset.order_by('-search_rank', '-created_at')
        return queryset

    def get_schema_operation_parameters(self, view):
        return [{
            'name': self.search_param,
            'required': False,
            'in': 'query',
            'description': 'جست‌وجو در نام و توضیحات محصول (تحمل غلط املایی)',
            'schema': {'type': 'string'},
        }]