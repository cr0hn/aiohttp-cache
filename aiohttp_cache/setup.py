import logging

from typing import Optional, Tuple, Union

import aioredis

from aiohttp import web

from . import AvailableKeys, MemoryCache, RedisCache, cache_middleware
from .backends import DEFAULT_KEY_PATTERN
from .exceptions import HTTPCache


log = logging.getLogger("aiohttp")


def setup_cache(
    app: web.Application,
    cache_type: str = "memory",
    key_pattern: Tuple[AvailableKeys, ...] = DEFAULT_KEY_PATTERN,
    encrypt_key: bool = True,
    redis: Optional[aioredis.Redis] = None,
    redis_url: Optional[str] = None,
) -> None:
    """Setup a cache for the application.

    Check examples of a setup at
    <https://github.com/cr0hn/aiohttp-cache#how-to-use-it>

    :param cache_type: could be "memory" or "redis"
    :param key_pattern: what to consider as identical request
    :param encrypt_key: encrypt the key in the caching backend
    :param backend_config: set a backend config
    """
    app.middlewares.append(cache_middleware)

    _cache_backend: Optional[Union[MemoryCache, RedisCache]] = None
    if cache_type.lower() == "memory":
        _cache_backend = MemoryCache(
            key_pattern=key_pattern, encrypt_key=encrypt_key
        )

        log.debug("Selected cache: {}".format(cache_type.upper()))

    elif cache_type.lower() == "redis":
        if redis is not None:
            _redis = redis
        elif redis_url:
            _redis = aioredis.from_url(redis_url)
        else:
            raise AssertionError(
                "The redis or redis_url parameter is required."
            )
        _cache_backend = RedisCache(
            redis=_redis,
            key_pattern=key_pattern,
            encrypt_key=encrypt_key,
        )

        log.debug("Selected cache: {}".format(cache_type.upper()))
    else:
        raise HTTPCache("Invalid cache type selected")

    app["cache"] = _cache_backend


__all__ = ("setup_cache",)
