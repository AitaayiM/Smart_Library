import django_filters
from personality.models import Personal
from django.db.models import Q

class PersonalFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name='user__roles__name', lookup_expr='iexact')
    gender = django_filters.CharFilter(field_name='user__gender', lookup_expr='iexact')
    full_name = django_filters.CharFilter(method='filter_by_full_name')
    date_of_birth_gte = django_filters.DateFilter(field_name="user__date_of_birth", lookup_expr="gte")
    date_of_birth_lte = django_filters.DateFilter(field_name="user__date_of_birth", lookup_expr="lte")
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')

    class Meta:
        model = Personal
        fields = []
    
    def filter_by_full_name(self, queryset, name, value):
        full_name = value.split(" ")
        first_name = full_name[0]
        last_name = full_name[-1] if len(full_name) > 1 else ""

        if first_name and last_name:
            return queryset.filter(
                Q(user__first_name__icontains=first_name) & Q(user__last_name__icontains=last_name) |
                Q(user__last_name__icontains=first_name) & Q(user__first_name__icontains=last_name) |
                Q(about_us__icontains=value) | Q(bio__icontains=value)
            )
        elif first_name:
            return queryset.filter(Q(user__first_name__icontains=first_name) | Q(user__last_name__icontains=first_name) |
                Q(about_us__icontains=value) | Q(bio__icontains=value))
        elif last_name:
            return queryset.filter(Q(user__last_name__icontains=last_name) | Q(user__first_name__icontains=last_name) |
                Q(about_us__icontains=value) | Q(bio__icontains=value))
        else:
            return queryset
