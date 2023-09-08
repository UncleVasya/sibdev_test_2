import datetime
import importlib
import json
import re

from django.conf import settings
from faker import Faker
from django.test import TestCase
import typing as t
import responses

from app.currency.tests.helpers import fake_decimal
from app.currency.cbr_client import CbrDailyApiClient
from app.currency.models import Currency, CurrencyPrice

fake = Faker(locale='ru')


class CbrApiClientTestCase(TestCase):
    """Кейс для проверки загрузки данных через api-сервис."""
    # количество дней для генерации истории
    history_days = 10
    # список валют
    currencies: t.List[t.Tuple[str, str]]
    # цены валют по датам в формате api
    prices_history: t.Dict[datetime.date, t.Dict]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # генерируем список валют
        n = 10
        cls.currencies = [fake.unique.currency() for _ in range(n)]

        # генерируем историю цен
        cls.prices_history = dict()
        today = datetime.date.today()
        for i in range(cls.history_days):
            d = today - datetime.timedelta(days=i)
            cls.prices_history[d] = cls._gen_api_currency_prices()

    def setUp(self):
        super().setUp()
        Currency.objects.all().delete()
        CurrencyPrice.objects.all().delete()

    @responses.activate
    def test_load_price_history(self) -> None:
        """Проверяет загрузку истории цен."""

        # мок ответа от api
        def request_callback(request):
            year, month, day = map(int, request.path_url.split('/')[2:5])
            date = datetime.date(year, month, day)
            data = self._api_prices_response(date)
            return 200, {}, json.dumps(data)

        url_regexp = r'/archive/\d{4}/\d{2}/\d{2}/daily_json.js'
        responses.add_callback(
            method=responses.GET,
            url=re.compile(settings.CBR_DAILY_API_HOST + url_regexp),
            callback=request_callback,
        )

        client = CbrDailyApiClient()
        client.load_price_history(days=self.history_days)

        # проверяем корректность сохраненных данных
        self.assert_currencies()
        self.assert_prices_history()

    @responses.activate
    def test_load_daily_prices(self) -> None:
        """Проверяет загрузку дневных котировок."""
        today = datetime.date.today()
        responses.get(
            CbrDailyApiClient.daily_url,
            json=self._api_prices_response(today),
        )

        client = CbrDailyApiClient()
        client.load_daily_prices()

        # проверяем корректность сохраненных данных
        self.assert_currencies()
        self.assert_daily_prices(date=today)


    @classmethod
    def _gen_api_currency_prices(cls) -> t.Dict[str, t.Dict]:
        """Генерирует цены валют в формате api."""
        return {
            char_code: {
                'ID': fake.pystr(max_chars=7),
                'NumCode': str(fake.pyint(max_value=1000)),
                'CharCode': char_code,
                'Nominal': fake.pyint(max_value=10),
                'Name': name,
                'Value': str(fake_decimal(max_value=100)),
                'Previous': str(fake_decimal(max_value=100)),
            }
            for char_code, name in cls.currencies
        }

    def _api_prices_response(self, date: datetime.date) -> t.Dict:
        """Генерирует ответ api с ценами валют за указанную дату."""
        dt = datetime.datetime(date.year, date.month, date.day)
        return {
            'Date': dt.isoformat(),
            'PreviousDate': fake.date_time().isoformat(),
            'PreviousURL': fake.url(),
            'Timestamp': dt.isoformat(),
            'Valute': self.prices_history[date],
        }

    def assert_currencies(self) -> None:
        """Проверяет валюты в БД на соответствие данным из api."""
        currencies = Currency.objects.all()

        for x in currencies:
            self.assertIn((x.char_code, x.name), self.currencies)

    def assert_prices_history(self) -> None:
        """Проверяет историю цен в БД на соответствие данным из api."""
        prices = CurrencyPrice.objects.all().select_related('currency')

        # проверяем, что все данные были сохранены
        self.assertEqual(len(prices),
            len(self.currencies) * self.history_days
        )
        # проверяем сохраненные значения цен
        self.assert_prices(prices)

    def assert_daily_prices(self, date: datetime.date) -> None:
        """Проверяет дневные котировки в БД на соответствие данным из api."""

        prices = CurrencyPrice.objects.filter(date=date).select_related('currency')

        self.assertEqual(len(prices), len(self.currencies))
        self.assert_prices(prices)


    def assert_prices(self, prices: t.List[CurrencyPrice]) -> None:
        """
        Проверяет цены валют из БД на соответстввие тому,
        что было получено из api.
        """
        for x in prices:
            date_data = self.prices_history[x.date]
            currency_data = date_data[x.currency.char_code]
            self.assertEqual(str(x.value), currency_data['Value'])
