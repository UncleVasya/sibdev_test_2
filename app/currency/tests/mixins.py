import datetime
import typing as t

from faker import Faker

from app.currency.models import Currency, CurrencyPrice
from app.currency.tests.factories import CurrencyFactory, CurrencyPriceFactory

fake = Faker(locale='ru')

class CurrencyMixin:
    """Миксин с методами для создания валют"""

    @classmethod
    def create_currencies(cls, n: int = 10) -> t.List[Currency]:
        """Создает список из n валют"""
        # здесь не подходит CurrencyFactory.create_batch()
        # из-за проблем с уникальностью
        return [
            CurrencyFactory(currency=fake.unique.currency())
            for _ in range(n)
        ]

class CurrenciesSetupMixin(CurrencyMixin):
    """Миксин с инициализацией валют в тест кейсе"""
    # noinspection PyPep8Naming
    @classmethod
    def setUpTestData(cls) -> None:
        # noinspection PyUnresolvedReferences
        super().setUpTestData()

        cls.currencies = cls.create_currencies()

    # noinspection PyPep8Naming
    @classmethod
    def tearDownClass(cls) -> None:
        # noinspection PyUnresolvedReferences
        super().tearDownClass()

        # сбрасываем список использованных значений между тестами
        fake.unique.clear()


class CurrencyPriceMixin:
    """Миксин с методами для создания записей о стоимости валют"""

    @classmethod
    def create_currency_price(cls, **kwargs) -> CurrencyPrice:
        """Создает запись о стоимости валюты"""
        return CurrencyPriceFactory(**kwargs)

    @classmethod
    def create_price_history(
        cls, currencies: t.List[Currency],  days: int = 10
    ):
        """Создает историю цен за n дней для переданных валют"""
        today = datetime.date.today()
        prices = []
        for i in range(days):
            date = today - datetime.timedelta(days=i)
            for currency in currencies:
                price = CurrencyPriceFactory(
                        date=date,
                        currency=currency,
                    )
                prices.append(price)

        cls.price_history_days = days

        return prices



class CurrencyPricesSetupMixin(CurrencyPriceMixin,
                               CurrenciesSetupMixin):
    """Миксин, заполняющий историю цен валют в тест кейсе"""
    # noinspection PyPep8Naming
    @classmethod
    def setUpTestData(cls):
        # noinspection PyUnresolvedReferences
        super().setUpTestData()

        # noinspection PyUnresolvedReferences
        cls.prices = cls.create_price_history(cls.currencies)
