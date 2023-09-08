import datetime

from django.db import IntegrityError
from django.test import TestCase

from app.currency.tests.factories import UserCurrencyFactory, CurrencyPriceFactory
from app.currency.tests.mixins import CurrenciesSetupMixin
from app.users.tests.mixins import UsersSetupMixin


class UserCurrencyTestCase(UsersSetupMixin,
                           CurrenciesSetupMixin,
                           TestCase):
    """Тесты модели для отслеживания пользователем валют"""

    def test_user_currency_unique_together(self):
        """Пользователь не может повторно добавить валюту к отслеживаемым."""
        UserCurrencyFactory(user=self.user, currency=self.currencies[0])
        with self.assertRaises(IntegrityError):
            UserCurrencyFactory(user=self.user, currency=self.currencies[0])


class CurrencyPriceTestCase(UsersSetupMixin,
                           CurrenciesSetupMixin,
                           TestCase):
    """Тесты модели стоимости валют"""

    def test_user_currency_unique_together(self):
        """Цена валюты должна быть уникальна для каждого дня"""
        today = datetime.date.today()
        CurrencyPriceFactory(date=today, currency=self.currencies[0])
        with self.assertRaises(IntegrityError):
            CurrencyPriceFactory(date=today, currency=self.currencies[0])
