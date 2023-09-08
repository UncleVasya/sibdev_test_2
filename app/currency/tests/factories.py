import datetime

import factory
from faker import Faker

from app.currency.tests.helpers import fake_decimal
from app.users.models import User

fake = Faker(locale='ru')

from app.currency import models


class CurrencyFactory(factory.django.DjangoModelFactory):
    """Фабрика для модели валют"""
    class Meta:
        model = models.Currency

    # служебное поле, используется только для заполнения полей ниже
    currency = fake.unique.currency()

    char_code = factory.LazyAttribute(lambda x: x.currency[0])
    name = factory.LazyAttribute(lambda x: x.currency[1])

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> models.Currency:
        # убираем служебное поле currency
        kwargs.pop('currency', None)
        return super()._create(model_class, *args, **kwargs)


class CurrencyPriceFactory(factory.django.DjangoModelFactory):
    """Фабрика для модели стоимости валют"""
    class Meta:
        model = models.CurrencyPrice

    date = factory.Faker('date', tzinfo=datetime.timezone.utc)
    currency = factory.Iterator(models.Currency.objects.all())
    value = factory.LazyAttribute(lambda x: fake_decimal())


class UserCurrencyFactory(factory.django.DjangoModelFactory):
    """Фабрика для модели отслеживания валюты пользователем"""
    class Meta:
        model = models.UserCurrency

    user = factory.Iterator(User.objects.all())
    currency = factory.Iterator(models.Currency.objects.all())
    threshold = factory.LazyAttribute(lambda x: fake_decimal())
