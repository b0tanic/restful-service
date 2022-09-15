import logging
from functools import partial
from types import AsyncGeneratorType, MappingProxyType
from typing import AsyncIterable, Mapping

from aiohttp import PAYLOAD_REGISTRY
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from configargparse import Namespace

from disk.api.handlers import HANDLERS
from disk.api.middleware import error_middleware, handle_validation_error
from disk.api.payloads import AsyncGenJSONListPayload, JsonPayload
from disk.utils.pg import setup_pg


# По умолчанию размер запроса к aiohttp ограничен 1 мегабайтом:
# https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application
# Размер тела запроса с 1 импортом (с учетом максимальной длины
# строк и кодировки json с параметром ensure_ascii=True) может занимать
# ~300 Байт
# Предположим, что максимальное число импортов за раз будет 200, тогда
# ~60 МБ:
MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 60 * MEGABYTE

log = logging.getLogger(__name__)


def create_app(args: Namespace) -> Application:
    """
    Создает экземпляр приложения, готового к запуску.
    """
    app = Application(
        client_max_size=MAX_REQUEST_SIZE,
        middlewares=[error_middleware, validation_middleware]
    )

    # Подключение на старте к postgres и отключение при остановке
    app.cleanup_ctx.append(partial(setup_pg, args=args))

    # Регистрация обработчиков
    for handler in HANDLERS:
        log.debug('Registering handler %r as %r', handler, handler.URL_PATH)
        app.router.add_route('*', handler.URL_PATH, handler)

    # Swagger документация
    setup_aiohttp_apispec(app=app, title='Disk API', swagger_path='/',
                          error_callback=handle_validation_error)

    # Автоматическая сериализация в json данных в HTTP ответах
    PAYLOAD_REGISTRY.register(AsyncGenJSONListPayload,
                              (AsyncGeneratorType, AsyncIterable))
    PAYLOAD_REGISTRY.register(JsonPayload, (Mapping, MappingProxyType))
    return app
