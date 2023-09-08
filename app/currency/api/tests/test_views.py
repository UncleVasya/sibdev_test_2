import datetime
import typing as t
from decimal import Decimal

from django.core.cache import cache
from django.db.models import Max, Min
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.currency.models import Currency, CurrencyPrice, UserCurrency
from app.currency.tests.factories import UserCurrencyFactory
from app.currency.tests.mixins import (CurrenciesSetupMixin,
                                       CurrencyPricesSetupMixin)
from app.users.models import User
from app.users.tests.mixins import UsersSetupMixin


class UserCurrencyCreateViewTestCase(UsersSetupMixin,
                                     CurrenciesSetupMixin,
                                     APITestCase):
    """Кейс для api добавления валюты в список отслеживаемых."""

    url = reverse('currency:user-currency')

    def setUp(self) -> None:
        super().setUp()

        UserCurrency.objects.all().delete()
        self.client.force_authenticate(self.user)

    def test_authentication_required(self) -> None:
        data = {
            'currency': self.currencies[0].id,
            'threshold': 100,
        }
        self.client.logout()
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_currency_success(self) -> None:
        """Проверяет добавление пользователем отслеживаемой валюты."""
        data = {
            'currency': self.currencies[0].id,
            'threshold': 100,
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        obj = UserCurrency.objects.last()
        self.assertEqual(obj.currency_id, data['currency'])
        self.assertEqual(obj.user_id, self.user.id)
        self.assertEqual(obj.threshold, data['threshold'])

    def test_cannot_add_same_currency_twice(self) -> None:
        """Проверяет, что нельзя повторно добавить уже отслеживаемую валюту."""
        data = {
            'currency': self.currencies[0].id,
            'threshold': 100,
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RatesViewTestCase(UsersSetupMixin,
                        CurrencyPricesSetupMixin,
                        APITestCase):
    """Кейс для api получения дневных котировок."""

    url = reverse('currency:rates')

    user: User
    user_currencies: t.List[UserCurrency]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # добавим пользователю несколько отслеживаемых валют
        # noinspection PyUnresolvedReferences
        cls.user_currencies = cls.currencies[:3]
        for currency in cls.user_currencies:
            UserCurrencyFactory(
                user=cls.user,
                currency=currency,
            )

    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(self.user)

        cache.clear()

    def test_user_with_tracked_currencies(self) -> None:
        """
        Проверяет получение дневных котировок пользователем,
        у которого есть валюты в списке отслеживаемых.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # проверяем, что в ответе содержатся данные только по отслеживаемым
        # валютам и что они верны
        expected_prices = CurrencyPrice.objects.filter(
            date=datetime.date.today(),
            currency__in=self.user_currencies,
        ).order_by('currency_id').select_related('currency')

        self.assert_prices_response(data, expected_prices)

    def test_user_without_tracked_currencies(self) -> None:
        """
        Если у пользователя пустой список отслеживаемых валют,
        api возвращает данные по всем валютам.
        """

        # создадим нового пользователя, у которого нет отслеживаемых валют
        user = self.create_user()

        self.client.logout()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # проверяем, что в ответе содержатся данные корректные данные
        # по всем валютам
        expected_prices = CurrencyPrice.objects.filter(
            date=datetime.date.today(),
        ).order_by('currency_id').select_related('currency')

        self.assert_prices_response(data, expected_prices)

    def test_anonymous_user(self) -> None:
        """
        Для неавторизованного пользователя api возвращает данные
        по всем валютам.
        """

        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # проверяем, что в ответе содержатся данные корректные данные
        # по всем валютам
        expected_prices = CurrencyPrice.objects.filter(
            date=datetime.date.today(),
        ).order_by('currency_id').select_related('currency')

        self.assert_prices_response(data, expected_prices)

    def test_order_by_value(self) -> None:
        """
        Проверяет возможность сортировки ответа api по стоимости валют.
        """

        cases = ['value', '-value']
        for case in cases:
            with self.subTest(order_by=case):
                params = {
                    'order_by': case,
                }
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                data = response.json()

                # проверяем, что данные в ответе api отсортированы верно
                expected_prices = CurrencyPrice.objects.filter(
                    date=datetime.date.today(),
                    currency__in=self.user_currencies,
                ).order_by(case).select_related('currency')

                self.assert_prices_response(data, expected_prices)

    def assert_prices_response(
            self,
            response_data: t.List[t.Dict],
            prices: t.List[CurrencyPrice],
    ) -> None:
        """
        Проверяет, что полученные в ответе api котировки соответствуют
        ожидаемым.
        """
        self.assertEqual(len(response_data), len(prices))
        for item, expected in zip(response_data, prices):
            self.assertEqual(item['date'], expected.date.isoformat())
            self.assertEqual(item['charcode'], expected.currency.char_code)
            self.assertEqual(item['id'], expected.currency_id)
            self.assertEqual(Decimal(str(item['value'])), expected.value)


class AnalyticsViewTestCase(UsersSetupMixin,
                            CurrencyPricesSetupMixin,
                            APITestCase):
    """Кейс для api получения аналитики по валюте."""

    user: User
    currency: Currency
    # user_currency: UserCurrency
    price_history_days: int


    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # noinspection PyUnresolvedReferences
        cls.currency = cls.currencies[0]
        cls.url = reverse(
            'currency:analytics',
            kwargs={'id': cls.currency.id}
        )

        # cls.user_currency = UserCurrencyFactory(
        #     user=cls.user,
        #     currency=currency,
        #     threshold=threshold,
        # )

    def setUp(self) -> None:
        super().setUp()
        self.client.force_authenticate(self.user)

    def test_authentication_required(self) -> None:
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_analytics_data(self) -> None:
        """Проверяет вычисление данных для api аналитики"""

        # подберем значение ПЗ, чтобы оно было в середине колебаний цены
        threshold = self.median_price(self.currency)

        params = {
            'threshold': threshold,
        }

        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), self.price_history_days)

        #  для проверки равенства float всегла следует приводить к Decimal
        max_value = max(x['value'] for x in data)
        max_value = Decimal(str(max_value))

        min_value = min(x['value'] for x in data)
        min_value = Decimal(str(min_value))

        # проверяем корректность аналитики
        for item in data:
            self.assertEqual(item['charcode'], self.currency.char_code)
            self.assertEqual(item['id'], self.currency.id)

            value = Decimal(str(item['value']))
            self.assertEqual(item['is_min_value'], value == min_value)
            self.assertEqual(item['is_max_value'], value == max_value)
            self.assertEqual(
                Decimal(str(item['percentage_ratio'])),
                round(value / threshold * 100, 2),
            )
            self.assertEqual(
                item['threshold_match_type'],
                'less' if value < threshold else
                'exceeded' if value > threshold else 'equal'
            )

    def test_date_range_filter(self) -> None:
        """Проверяет работу фильтра по интервалу дат."""

        today = datetime.date.today()
        params = {
            'date_from': (today - datetime.timedelta(days=5)).isoformat(),
            'date_to': (today - datetime.timedelta(days=2)).isoformat(),
        }

        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        min_date = min(x['date'] for x in data)
        max_date = max(x['date'] for x in data)
        
        self.assertEqual(min_date, params['date_from'])
        self.assertEqual(max_date, params['date_to'])

    def median_price(self, currency: Currency) -> Decimal:
        """
        Вычисляет медиану цены валюты.
        Используется для задания хорошего ПЗ для теста аналитики.
        """
        qs = CurrencyPrice.objects.filter(
            currency=currency
        ).order_by('value')

        values = qs.values_list('value', flat=True)
        count = len(values)
        position = int(round(count / 2))

        return values[position]