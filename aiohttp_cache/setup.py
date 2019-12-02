import logging
from typing import Tuple

from aiohttp import web
from envparse import env

from .backends import *
from .exceptions import *
from .middleware import *

log = logging.getLogger("aiohttp")
env.read_envfile(".env")


def setup_cache(
    app: web.Application,
    cache_type: str = "memory",
    key_pattern: Tuple[AvailableKeys] = DEFAULT_KEY_PATTERN,
    encrypt_key=True,
    backend_config=None,
):
    app.middlewares.append(cache_middleware)

    _cache_backend = None
    if cache_type.lower() == "memory":
        _cache_backend = MemoryCache(
            key_pattern=key_pattern, encrypt_key=encrypt_key
        )

        log.debug("Selected cache: {}".format(cache_type.upper()))

    elif cache_type.lower() == "redis":
        _redis_config = backend_config or RedisConfig()

        assert isinstance(
            _redis_config, RedisConfig
        ), "Config must be a RedisConfig object. Got: '{}'".format(
            type(_redis_config)
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
