from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab

env = environ.Env()
environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('SECRET_KEY', default='woof')

DEBUG = env.bool('DEBUG', default=True)
TESTING = env.bool('TESTING', default=False)

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', default='localhost').split(' ')

REDIS_URL = env('REDIS_URL', default='redis://redis:6379/0')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',
    'djoser',

    'app.currency',
    'app.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'sibdev_test_2.urls'
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sibdev_test_2.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='postgresql'),
        'USER': env('DB_USER', default='postgresql'),
        'PASSWORD': env('DB_PASSWORD', default='postgresql'),
        'HOST': env('DB_HOST', default='db'),
        'PORT': env('DB_PORT', default='5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        },
        'TIMEOUT': 36000,
    }
}

# Для тестов используем эмулятор redis-a, чтобы не требовать поднятый настоящий
if TESTING:
    from fakeredis import FakeConnection
    CACHES['default']['BACKEND'] = 'django.core.cache.backends.redis.RedisCache'
    # noinspection PyTypedDict
    CACHES['default']['OPTIONS'] = {'connection_class': FakeConnection}


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'ORDERING_PARAM': 'order_by',
}

JWT_ACCESS_TOKEN_LIFETIME = env('JWT_ACCESS_TOKEN_LIFETIME', default=5)
JWT_REFRESH_TOKEN_LIFETIME = env('JWT_REFRESH_TOKEN_LIFETIME', default=360)
SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
   'ACCESS_TOKEN_LIFETIME': timedelta(minutes=JWT_ACCESS_TOKEN_LIFETIME),
   'REFRESH_TOKEN_LIFETIME': timedelta(minutes=JWT_REFRESH_TOKEN_LIFETIME),
}

AUTH_USER_MODEL = 'users.User'

DJOSER = {
    'LOGIN_FIELD': 'email',
}

CBR_DAILY_API_HOST = env(
    'CBR_DAILY_API_HOST',
    default='https://www.cbr-xml-daily.ru',
)


CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
CELERY_TASK_ALWAYS_EAGER = TESTING
CELERY_BROKER_URL = env('CELERY_BROKER', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_BROKER', default='redis://redis:6379/0')

CELERY_BEAT_SCHEDULE = {
    'load-daily-prices': {
        'task': 'currency.load_daily_prices',
        'schedule': crontab(minute='0', hour='12'),
    },
}

