from app.users.models import User
from app.users.tests.factories import UserFactory


class UsersMixin:
    """Миксин с методами для создания пользователей"""
    @classmethod
    def create_user(cls, **kwargs) -> User:
        """Создает пользователя с переданными атрибутами"""
        return UserFactory(**kwargs)


class UsersSetupMixin(UsersMixin):
    """Миксин с инициализацией пользователей в тест кейсе"""
    # noinspection PyPep8Naming
    @classmethod
    def setUpTestData(cls) -> None:
        # noinspection PyUnresolvedReferences
        super().setUpTestData()
        cls.user = cls.create_user()