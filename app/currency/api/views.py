from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.cache import cache
from django.db.models import (
    QuerySet, Subquery, Window, Max, F, Value, Case,
    When, ExpressionWrapper, Q, Min, DecimalField
)
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework import permissions
from rest_framework.response import Response
import typing as t
from app.currency.api import serializers, const
from app.currency.api.filters import DateRangeFilter
from app.currency.models import UserCurrency, CurrencyPrice
from app.tools.helpers import cache_per_user
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class UserCurrencyCreateView(generics.CreateAPIView):
    """API для добавления пользователем отслеживаемой валюты."""
    queryset = UserCurrency.objects.all()
    serializer_class = serializers.UserCurrencySerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='order_by',
            description='Поле для сортировки списка квот',
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            enum=['value', '-value'],
        ),
    ]
)
class RatesView(generics.ListAPIView):
    """API для отображения последних загруженных котировок."""
    serializer_class = serializers.RatesSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ['value']

    def get_queryset(self) -> QuerySet:
        """
        Возвращает qs с последними загруженными котировками
        для каждой валюты.
        """
        return CurrencyPrice.objects.filter(
            pk__in=Subquery(
                CurrencyPrice.objects
                  .order_by('currency_id')
                  .distinct('currency_id')
                  .values('pk')
            )
        ).order_by('currency_id', '-date')

    @method_decorator(cache_per_user(const.cache_timeout))
    def list(self, request: HttpRequest, *args, **kwargs) -> Response:
        """
        Возвращает ответ api со списком последних загруженных котировок,
        отфильтрованных по списку валют пользователя.
        Используется 2 уровня кеша:
        - кеш для полного списка последних котировок (одинаков для всех пользователей);
        - кеш ответа для каждого пользователя (декоратор);
        Оба кеша учитывают параметры запроса.
        """
        cache_key = f'{const.rates_cache_key}:{request.get_full_path()}'
        rates = cache.get(key=cache_key)
        if rates is None:
            # в кеше пусто, заполняем кеш
            qs = self.filter_queryset(self.get_queryset())
            rates = list(qs)
            cache.set(key=cache_key, value=rates)

        rates = self._filter_by_user(rates, self.request.user)

        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)

    @staticmethod
    def _filter_by_user(
        rates: t.List[CurrencyPrice],
        user: t.Type[AbstractUser] | AnonymousUser,
    ) -> t.List[CurrencyPrice]:
        """
        Фильтрует список котировок по списку валют пользователя.
        Для анонимного пользователя возвращает полный список.
        Если в списке валют пользователя пусто, то возвращает все котировки.
        """
        if user.is_authenticated:
            tracked = (
                UserCurrency.objects
                  .filter(user=user)
                  .values_list('currency_id', flat=True)
            )
            if tracked:
                rates = [
                    x for x in rates if x.currency_id in tracked
                ]
        return rates


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='threshold',
            description='Пороговое значение цены',
            required=False,
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name='date_from',
            description='Начальная дата выборки',
            required=False,
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name='date_to',
            description='Конечная дата выборки',
            required=False,
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name='id',
            description='id валюты',
            required=True,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
        ),
    ]
)
class AnalyticsView(generics.ListAPIView):
    """API для отображения аналитики по конкретной валюте."""
    serializer_class = serializers.AnalyticsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DateRangeFilter
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        """
        Фильтрует qs с ценами по id валюты, а также
        обогащает его данными для аналитики.
        """
        currency_id = self.kwargs.get('id')
        qs = CurrencyPrice.objects.filter(
           currency_id=currency_id
        )
        qs = self._add_analytics(qs)

        return qs

    def _add_analytics(self, queryset: QuerySet) -> QuerySet:
        """Добавляет аналитические данные в qs."""
        threshold = self.request.query_params.get('threshold')
        if threshold:
            # признак превышения котировкой порогового значения
            threshold_match_expr = Case(
                When(value__gt=threshold, then=Value('exceeded')),
                When(value__lt=threshold, then=Value('less')),
                default=Value('equal'),
            )
            # процентное отношение котировки к пороговому значению;
            # при вычислении процента учитываем, что в threshold может быть 0
            # и это может вызвать ошибку деления на 0
            threshold_percent_expr = (
                F('value') / Value(threshold) * 100 if float(threshold) > 0
                else Value(None)
            )

            queryset = queryset.annotate(
                threshold_match_type=threshold_match_expr,
                percentage_ratio=ExpressionWrapper(
                    threshold_percent_expr,
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )

        # признак максимальной и минимальной котировки в выборке
        max_value_expr = Window(
            expression=Max('value'),
            partition_by=(F('currency_id'),)
        )
        min_value_expr = Window(
            expression=Min('value'),
            partition_by=(F('currency_id'),)
        )

        return queryset.annotate(
            is_max_value=Q(value=max_value_expr),
            is_min_value=Q(value=min_value_expr),
        )
