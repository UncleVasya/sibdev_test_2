import time
from urllib.parse import urljoin

import requests
from django.conf import settings

from app.currency.models import Currency, CurrencyPrice
import typing as t
from logging import getLogger
from datetime import date, datetime, timedelta

logger = getLogger(__name__)


class CbrDailyApiClient:
    """Клиент API для сервиса cbr-xml-daily.ru"""
    archive_endpoint = 'archive/{year}/{month:02d}/{day:02d}/daily_json.js'
    archive_url = urljoin(settings.CBR_DAILY_API_HOST, archive_endpoint)

    daily_endpoint = 'daily_json.js'
    daily_url = urljoin(settings.CBR_DAILY_API_HOST, daily_endpoint)

    currencies: t.Dict[str, dict] = dict()

    def load_price_history(
        self, days: int = 30, progress_callback: t.Callable = None
    ) -> None:
        """
        Загружает котировки для всех валют за указанное количество дней.
        На каждом шаге вызывает callback для передачи информации о прогрессе.
        """
        today = date.today()

        prices = []
        for i in range(days):
            d = today - timedelta(days=i)
            url = self.archive_url.format(year=d.year, month=d.month, day=d.day)

            data = None
            try:
                r = requests.get(url)
                data = r.json()
                error = data.get('error')
            except Exception as e:
                error = str(e)

            if progress_callback:
                progress_callback(step_date=d, url=url, error=error)

            if error:
                logger.error(error)
                continue

            if not self.currencies:
                self._update_currencies(data['Valute'])

            prices += self._parse_prices(data)
            time.sleep(0.1)  # не ддосим сервис

        self._update_prices(prices)

    def load_daily_prices(self) -> None:
        """Загружает котировки для всех валют за сегодняшний день."""
        try:
            r = requests.get(self.daily_url)
            data = r.json()
        except Exception as e:
            logger.error(e)
            return

        if not self.currencies:
            self._update_currencies(data['Valute'])

        prices = self._parse_prices(data)
        self._update_prices(prices)

    def _update_currencies(self, data: t.Dict[str, t.Dict]) -> None:
        """Заполняет таблицу доступных валют."""
        currencies = [
            Currency(char_code=x['CharCode'], name=x['Name'])
            for x in data.values()
        ]
        Currency.objects.bulk_create(
            objs=currencies,
            ignore_conflicts=True,
        )
        # обновляем данные из базы для получения id объектов
        currencies = Currency.objects.all()

        self.currencies = {
            x.char_code: x for x in currencies
        }

    def _update_prices(self, prices: t.List[CurrencyPrice]) -> None:
        """Сохраняет распарсенные котировки в БД одним запросом."""
        CurrencyPrice.objects.bulk_create(
            objs=prices,
            update_conflicts=True,
            unique_fields=['date', 'currency_id'],
            update_fields=['value']
        )

    def _parse_prices(self, data: t.Dict) -> t.List[CurrencyPrice]:
        """Парсит json с информацией о котировках в модель CurrencyPrice."""
        date = datetime.fromisoformat(data['Date']).date()
        return [
            CurrencyPrice(
                date=date,
                currency=self.currencies[x['CharCode']],
                value=x['Value']
            )
            for x in data['Valute'].values()
        ]
