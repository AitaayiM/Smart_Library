import django_filters
from django.utils import timezone
from identity.models import User

class UserFilter(django_filters.FilterSet):
    gender = django_filters.CharFilter(lookup_expr='iexact')
    date_of_birth_gte = django_filters.DateFilter(field_name="date_of_birth" or 0000-00-00, lookup_expr="gte")
    date_of_birth_lte = django_filters.DateFilter(field_name="date_of_birth" or timezone.now().date(), lookup_expr="lte")

    class Meta:
        model = User
        fields = []