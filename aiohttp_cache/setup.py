import logging

from typing import Optional, Tuple, Union

from aiohttp import web

from aiohttp_cache import (
    AvailableKeys,
    MemoryCache,
    RedisCache,
    RedisConfig,
    cache_middleware,
)
from aiohttp_cache.backends import DEFAULT_KEY_PATTERN
from aiohttp_cache.exceptions import HTTPCache


log = logging.getLogger("aiohttp")


def setup_cache(
    app: web.Application,
    cache_type: str = "memory",
    key_pattern: Tuple[AvailableKeys, ...] = DEFAULT_KEY_PATTERN,
    encrypt_key: bool = True,
    backend_config: Optional[RedisConfig] = None,
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
        _redis_config = backend_config or RedisConfig()

        if not isinstance(_redis_config, RedisConfig):
            raise AssertionError(
                f"Config must be a RedisConfig object. Got: "
                f"'{type(_redis_config)}'"
            )
        _cache_backend = RedisCache(
            config=_redis_config,
            key_pattern=key_pattern,
            encrypt_key=encrypt_key,
        )

        log.debug("Selected cache: {}".format(cache_type.upper()))
    else:
        raise HTTPCache("Invalid cache type selected")

    app["cache"] = _cache_backend


__all__ = ("setup_cache",)
