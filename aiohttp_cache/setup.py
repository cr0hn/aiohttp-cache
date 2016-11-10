import logging

from aiohttp import web

from .backends import *
from .middleware import *
from .exceptions import *

log = logging.getLogger("aiohttp")


def setup_cache(app: web.Application,
                cache_type: str = "memory",
                backend_config=None):
    app.middlewares.append(cache_middleware)
    
    _cache_backend = None
    if cache_type.lower() == "memory":
        _cache_backend = MemoryCache()
        
        log.debug("Selected cache: {}".format(cache_type.upper()))
        
    elif cache_type.lower() == "redis":
        _redis_config = backend_config or RedisConfig()
        
        assert isinstance(_redis_config, RedisConfig), \
            "Config must be a RedisConfig object. Got: '{}'".format(type(_redis_config))
        _cache_backend = RedisCache(config=_redis_config)
        
        log.debug("Selected cache: {}".format(cache_type.upper()))
    else:
        raise HTTPCache("Invalid cache type selected")
    
    app["cache"] = _cache_backend


__all__ = ("setup_cache", )
