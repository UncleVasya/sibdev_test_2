from functools import wraps

from django.views.decorators.cache import cache_page


def cache_per_user(timeout=None):
    """
    Декоратор, который кеширует страницы с разделением по пользователям.
    Основано на https://stackoverflow.com/a/53209538.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_id = 'anonymous'
            if request.user.is_authenticated:
                user_id = request.user.id

            return cache_page(
                timeout,
                key_prefix=f'_user_{user_id}_',
            )(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator
