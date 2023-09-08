import datetime
import logging

from django.core.management.base import BaseCommand
from tqdm import tqdm

from app.currency.cbr_client import CbrDailyApiClient
from app.currency.helpers import clear_api_cache
from app.currency.tasks import send_threshold_emails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Загружает историю цен всех котируемых валют.'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '-d', '--days', nargs='?', type=int, default=30,
            help='Количество дней, для которых загрузить котировки.'
        )
        parser.add_argument(
            '-f', '--force_emails', nargs='?', type=bool,
            default=False, const=True,
            help='Принудительно отправить имейлы, даже если они '
                 'сегодня уже отправлялись.'
        )

    def handle(self, *args, **options) -> None:
        days = options['days']
        errors = 0

        def progress_callback(
                step_date: datetime.date, url: str, error: str = None
        ) -> None:
            """Callback для получения информации о прогрессе загрузки."""
            pbar.update(1)
            if error:
                logger.error(
                    f'\nНе удалось загрузить данные за {step_date.isoformat()}. \n'
                    f'url: {url} \n'
                    f'Ошибка: {error}\n'
                    '-------------------\n'
                )
                nonlocal errors
                errors += 1

        with tqdm(total=days) as pbar:
            client = CbrDailyApiClient()
            client.load_price_history(
                days=days,
                progress_callback=progress_callback,
            )

        # отправляем имейлы
        send_threshold_emails.delay(force=options['force_emails'])
        # очищаем кеши представлений для api
        clear_api_cache()

        logger.info(
            f'\nДанные загружены.\n'
            f'Обработано дней: {days}\n'
            f'Количество ошибок: {errors}\n'
        )








