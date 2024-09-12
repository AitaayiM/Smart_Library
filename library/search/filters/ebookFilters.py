import django_filters
from django.db import models 
from django.utils import timezone

from library.settings import BASE_DIR
import os

from ebook.models import EBook

class EbookFilter(django_filters.FilterSet):
    minPage = django_filters.filters.NumberFilter(field_name="pages" or 0, lookup_expr="gte")
    maxPage = django_filters.filters.NumberFilter(field_name="pages" or 1000000, lookup_expr="lte")
    published_at = django_filters.filters.DateFilter(field_name="published_at" or 0000-00-00, lookup_expr="gte")
    minRating = django_filters.filters.NumberFilter(field_name="ratings" or 0, lookup_expr="gte")
    maxRating = django_filters.filters.NumberFilter(field_name="ratings" or 5, lookup_expr="lte")

    class Meta:
        model = EBook
        fields = []

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        current_date = timezone.now().date()
        queryset = queryset.filter(published_at__lte = current_date)
        return queryset