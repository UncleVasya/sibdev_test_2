from django_filters import rest_framework


class DateRangeFilter(rest_framework.FilterSet):
    date_from = rest_framework.DateFilter(
        field_name='date',
        lookup_expr='gte',
    )
    date_to = rest_framework.DateFilter(
        field_name='date',
        lookup_expr='lte',
    )

    class Meta:
        fields = ['date_from', 'date_to']
