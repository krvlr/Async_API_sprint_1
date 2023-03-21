import logging
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from inspect import signature
from typing import Callable, Any

from core.config import settings
from services.base import Service
from utils.cache_serializer import PickleCacheSerializer
from utils.exceptions import ClientNotInitializedException, CachingException

logger = logging.getLogger(__name__)


@dataclass
class CacheData:
    saved_datetime: datetime
    data: Any


def _get_cache_key(self, func: Callable, *args: list, **kwargs: dict) -> str:
    func_args = signature(func).bind(self, *args, **kwargs)
    func_args.apply_defaults()

    func_args_str = ",".join(
        f"{arg}={val}" for arg, val in func_args.arguments.items() if arg != "self"
    )

    return f"{self.__class__.__name__}.{func.__name__}.({func_args_str})"


async def _get_cache_data(redis, cache_key: str, expire: int) -> Any:
    cache_data = await redis.get(cache_key)
    if cache_data:
        cache_data: CacheData = PickleCacheSerializer.deserialize(cache_data)
        if (datetime.now() - cache_data.saved_datetime).seconds < expire:
            return cache_data.data
        else:
            return None


async def _set_cache_data(redis, cache_key: str, data: Any) -> Any:
    cache_data = CacheData(saved_datetime=datetime.now(), data=data)
    await redis.set(cache_key, PickleCacheSerializer.serialize(cache_data))


def cache(expire=settings.cache_expire_in_seconds) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not isinstance(self, Service):
                raise CachingException(
                    "Класс должен наследовать Service, для того, чтобы быть закешированным"
                )
            if not self.redis:
                raise ClientNotInitializedException("Клиент redis не инициализирован")

            cache_key = _get_cache_key(self, func, *args, **kwargs)
            cache_data = await _get_cache_data(self.redis, cache_key, expire)

            if cache_data is not None:
                return cache_data
            else:
                data = await func(self, *args, **kwargs)
                if data is None:
                    return None
                await _set_cache_data(self.redis, cache_key, data)
                return data

        return wrapper

    return decorator
