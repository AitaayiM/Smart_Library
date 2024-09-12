import django_filters
from django.utils import timezone
from personality.models import Post

class PostFilter(django_filters.FilterSet):
    content = django_filters.CharFilter(field_name="content", lookup_expr="icontains")
    
    class Meta:
        model = Post
        fields = []

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        current_date = timezone.now().date()
        queryset = queryset.filter(published_at__lte = current_date)
        return queryset

