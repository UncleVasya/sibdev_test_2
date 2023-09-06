from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.cache import cache
from django.db.models import QuerySet, Subquery
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
import typing as t
from app.currency.api import serializers, const
from app.currency.api.const import cache_timeout
from app.currency.models import UserCurrency, CurrencyPrice
from app.tools.helpers import cache_per_user


class UserCurrencyCreateView(generics.CreateAPIView):
    """Представление для добавления пользователем отслеживаемой валюты."""
    queryset = UserCurrency.objects.all()
    serializer_class = serializers.UserCurrencySerializer


class RatesView(generics.ListAPIView):
    """Представление для отображения последних загруженных котировок."""
    serializer_class = serializers.DailyPricesSerializer
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
        """
        cache_key = f'{const.rates_cache_key}:{request.get_full_path()}'
        rates = cache.get(key=cache_key)
        if rates is None:
            print(f'writing {cache_key}')
            qs = self.filter_queryset(self.get_queryset())
            rates = list(qs)
            cache.set(key=cache_key, value=rates)
        else:
            print(f'reading {cache_key}')

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

