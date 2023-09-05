from django.core.management.base import BaseCommand
from tqdm import tqdm

from app.currency.cbr_daily_api_client import CbrDailyApiClient
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Загружает историю цен всех котируемых валют.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--days', nargs='?', type=int, default=30, const=30,
            help='Количество дней, для которых загрузить котировки.'
        )

    def handle(self, *args, **options):
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

        logger.info(
            f'\nДанные загружены.\n'
            f'Обработано дней: {days}\n'
            f'Количество ошибок: {errors}\n'
        )








