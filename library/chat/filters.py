import django_filters
from django.db.models import Q
from django.utils import timezone
from .models import Message

class MessageFilter(django_filters.FilterSet):
    keyword = django_filters.CharFilter(method="filter_by_keyword")
    date_gte = django_filters.DateFilter(field_name="timestamp" or 0000-00-00, lookup_expr="gte")
    date_lte = django_filters.DateFilter(field_name="timestamp" or timezone.now().date(), lookup_expr="lte")
    
    class Meta:
        model = Message
        fields = ("keyword", "date_gte", "date_lte")
    
    def filter_by_keyword(self, queryset, name, value):
        return queryset.filter(Q(content__icontains=value))