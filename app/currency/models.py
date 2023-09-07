import datetime

from django.db import models

from app.users.models import User
from solo.models import SingletonModel


class Currency(models.Model):
    char_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.char_code}: {self.name}'

    class Meta:
        ordering = ('char_code',)


class CurrencyPrice(models.Model):
    date = models.DateField()
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='prices',
    )
    value = models.DecimalField(decimal_places=4, max_digits=10)

    class Meta:
        unique_together = ('date', 'currency')
        ordering = ('-date', 'currency')

    def __str__(self):
        return (
            f'{self.date.isoformat()} | '
            f'{self.currency.char_code} | '
            f'{self.value}'
        )


class UserCurrency(models.Model):
    """Модель для отслеживания пользователем стоимости валют."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    threshold = models.DecimalField(decimal_places=4, max_digits=10)

    class Meta:
        ordering = ('currency',)
        unique_together = ('user', 'currency')


class CommonData(SingletonModel):
    price_email_latest_date = models.DateField(
        default=datetime.date.fromisoformat('2000-01-01')
    )
