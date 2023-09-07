from django.utils.cache import add_never_cache_headers


class DisableBrowserCachingMiddleware(object):
    """
    Отключает кеш на стороне браузера.
    Во время разработки нужно часто переключаться между пользователями
    и одни и те же api могут вернуть разные данные для разных пользователей.
    Кеш браузера это не учитывает и возвращает закешированный ответ api
    для другого пользователя.
    Поэтому на время активной разработки его лучше отключить.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Pragma'] = 'no-cache'
        add_never_cache_headers(response)

        return response
