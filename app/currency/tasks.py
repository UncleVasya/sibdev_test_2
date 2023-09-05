from sibdev_test_2.celery import app

from app.currency.cbr_daily_api_client import CbrDailyApiClient


@app.task(name='currency.load_daily_prices')
def load_daily_prices():
    """ Задача для загрузки последних котировок."""
    client = CbrDailyApiClient()
    client.load_daily_prices()
