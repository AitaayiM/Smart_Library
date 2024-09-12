import django_filters
from django.utils import timezone
from personality.models import Share

class ShareFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(field_name="post__content", lookup_expr="icontains")
    
    class Meta:
        model = Share
        fields = []

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        current_date = timezone.now().date()
        queryset = queryset.filter(post__published_at__lte = current_date)
        return queryset