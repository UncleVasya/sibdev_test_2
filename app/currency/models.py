from django.db import models


class Currency(models.Model):
    char_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.char_code}: {self.name}'


class CurrencyPrice(models.Model):
    date = models.DateField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    value = models.DecimalField(decimal_places=4, max_digits=10)

    class Meta:
        unique_together = ('date', 'currency')

    def __str__(self):
        return (
            f'{self.date.isoformat()} | '
            f'{self.currency.char_code} | '
            f'{self.value}'
        )

