import django_filters
from django.utils import timezone
from django.db.models import Q
from .models import EBook

class EbookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="iexact")
    keyword = django_filters.CharFilter(method="filter_by_keyword")
    minPage = django_filters.NumberFilter(field_name="pages" or 0, lookup_expr="gte")
    maxPage = django_filters.NumberFilter(field_name="pages" or 1000000, lookup_expr="lte")
    published_at = django_filters.DateFilter(field_name="published_at" or 0000-00-00, lookup_expr="gte")
    minRating = django_filters.NumberFilter(field_name="ratings" or 0, lookup_expr="gte")
    maxRating = django_filters.NumberFilter(field_name="ratings" or 5, lookup_expr="lte")
    
    class Meta:
        model = EBook
        fields = ("keyword", "pages", "category", "ratings", "published_at")

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # Filter out ebooks where published_at is in the past
        current_date = timezone.now().date()
        queryset = queryset.filter(published_at__lte = current_date)
        
        return queryset
    
    def filter_by_keyword(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) |
                               Q(summary__icontains=value) |
                               Q(content_txt__icontains=value)
                            )