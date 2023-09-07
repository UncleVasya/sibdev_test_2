import datetime
from itertools import groupby

from django.conf import settings
from django.db.models import F, Max, Q
from django.template.loader import render_to_string
from post_office import mail

from app.currency.cbr_client import CbrDailyApiClient
from app.currency.helpers import clear_api_cache
from app.currency.models import CommonData, UserCurrency
from sibdev_test_2.celery import app


@app.task(name='currency.load_daily_prices')
def load_daily_prices() -> None:
    """ Задача для загрузки последних котировок."""
    client = CbrDailyApiClient()
    client.load_daily_prices()

    # отправляем имейлы
    send_threshold_emails.delay()
    # очищаем кеши представлений для api
    clear_api_cache()


@app.task(name='currency.send_threshold_emails')
def send_threshold_emails(force: bool = False) -> None:
    """
    Задача для отправки email-ов тем пользователям,
    чьи ПЗ были превышены в новых загруженных котировках.
    """
    email_template = 'currency/email/threshold_exceeded_email.html'

    # проверяем, что мы еще не отправляли email-ы сегодня
    common = CommonData.get_solo()
    today = datetime.date.today()

    if common.price_email_latest_date == today and not force:
        return # имейлы уже отправлялись сегодня

    # определяем валюты с превышением ПЗ по пользователям
    qs = UserCurrency.objects.annotate(
        value=Max(
            'currency__prices__value',
            filter=Q(currency__prices__date=today)
        ),
        user_email=F('user__email'),
    ).select_related(
        'currency'
    ).filter(
        value__gt=F('threshold')
    ).order_by('user')

    # группируем данные по пользователю для удобной отправки сообщений
    grouped = groupby(qs, key=lambda x: x.user_email)

    for user_email, prices in grouped:
        context = {
            'prices': list(prices),
        }
        html_message = render_to_string(email_template, context)

        mail.send(
            sender=settings.DEFAULT_FROM_EMAIL,
            recipients=[user_email],
            subject=f'Превышения ПЗ котировок за {today.isoformat()}',
            html_message=html_message,
        )


    common.price_email_latest_date = today
    common.save()
