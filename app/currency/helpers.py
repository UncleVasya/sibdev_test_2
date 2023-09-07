from django.core.cache import cache

from app.currency.api import const


def clear_api_cache() -> None:
    """Очищает кеши представлений для api."""

    keys = cache.keys(f'*{const.rates_cache_key}*')
    keys += cache.keys('*views.decorators.cache*')
    cache.delete_many(keys=keys)
