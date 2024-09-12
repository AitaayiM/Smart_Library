import django_filters
from personality.models import Invitation

class InvitationFilter(django_filters.FilterSet):
    sent = django_filters.CharFilter(method='get_sent_invitations')
    received = django_filters.CharFilter(method='get_received_invitations')
    type = django_filters.CharFilter(field_name='type', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')

    class Meta:
        model = Invitation
        fields = []

    def get_sent_invitations(self, queryset, name, value):
        if value:
            return queryset.filter(from_personal__user__id=value)
        return queryset

    def get_received_invitations(self, queryset, name, value):
        if value:
            return queryset.filter(to_personal__user__id=value)
        return queryset
