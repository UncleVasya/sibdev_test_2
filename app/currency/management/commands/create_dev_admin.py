import logging

from django.core.management.base import BaseCommand

from app.users.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: скрипт должен проверять, что мы находимся на dev-окружении
class Command(BaseCommand):
    help = (
        'Если список пользователей в БД пуст,'
        'то создает админа со стандартным паролем.'
    )

    def handle(self, *args, **options) -> None:
        logger.info('Создаем тестового админа...')

        if User.objects.exists():
            logger.info('База не пуста. Админа создавать не нужно.')
            return

        admin = User.objects.create(
            email='admin@test.com',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        admin.set_password('admin')
        admin.save()

        logger.info('Создан тестовый админ.')