import factory

from app.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    last_name = factory.Faker('last_name', locale='ru_RU')
    first_name = factory.Faker('first_name', locale='ru_RU')
    password = factory.PostGenerationMethodCall('set_password', 'test')
    is_active = True

