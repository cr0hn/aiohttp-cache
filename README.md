# Aiohttp-cache
title: 'aiohttp-cache'
---

![aiohttp-cache logo](https://raw.githubusercontent.com/cr0hn/aiohttp-cache/master/doc/source/_static/aiohttp-cache-128x128.png)


# What's aiohttp-cache

`aiohttp-cache` is a plugin for aiohttp.web server that allow to use a
cache system to improve the performance of your site.

# How to use it

## With in-memory backend

```python
import asyncio

from aiohttp import web

from aiohttp_cache import (  # noqa
    setup_cache,
    cache,
)

PAYLOAD = {"hello": "aiohttp_cache"}
WAIT_TIME = 2


@cache()
async def some_long_running_view(request: web.Request) -> web.Response:
    await asyncio.sleep(WAIT_TIME)
    payload = await request.json()
    return web.json_response(payload)


app = web.Application()
setup_cache(app)
app.router.add_post("/", some_long_running_view)

web.run_app(app)
```

## With redis backend

**Note**: redis should be available at
 `$CACHE_URL` env variable or`redis://localhost:6379/0`

```python
import asyncio

import yarl
from aiohttp import web
from envparse import env

from aiohttp_cache import (  # noqa
    setup_cache,
    cache,
    RedisConfig,
)

PAYLOAD = {"hello": "aiohttp_cache"}
WAIT_TIME = 2


@cache()
async def some_long_running_view(request: web.Request) -> web.Response:
    await asyncio.sleep(WAIT_TIME)
    payload = await request.json()
    return web.json_response(payload)


app = web.Application()
url = yarl.URL(env.str("CACHE_URL", default="redis://localhost:6379/0"))
setup_cache(
    app,
    cache_type="redis",
    backend_config=RedisConfig(
        db=int(url.path[1:]), host=url.host, port=url.port
    ),
)

app.router.add_post("/", some_long_running_view)

web.run_app(app)
```

## Example with a custom cache key

Let's say you would like to cache the requests just by the method and
json payload, then you can setup this as per the follwing example.

**Note** default key_pattern is:

```python
DEFAULT_KEY_PATTERN = (
    AvailableKeys.method,
    AvailableKeys.host,
    AvailableKeys.path,
    AvailableKeys.postdata,
    AvailableKeys.ctype,
)
```

```python
import asyncio

from aiohttp import web

from aiohttp_cache import setup_cache, cache, AvailableKeys  # noqa

PAYLOAD = {"hello": "aiohttp_cache"}
WAIT_TIME = 2


@cache()
async def some_long_running_view(request: web.Request) -> web.Response:
    await asyncio.sleep(WAIT_TIME)
    payload = await request.json()
    return web.json_response(payload)


custom_cache_key = (AvailableKeys.method, AvailableKeys.json)

app = web.Application()
setup_cache(app, key_pattern=custom_cache_key)
app.router.add_post("/", some_long_running_view)

web.run_app(app)
```

# License

This project is released under BSD license. Feel free

# Source Code

The latest developer version is available in a github repository:
<https://github.com/cr0hn/aiohttp-cache>

# Development environment

1.  docker-compose run tests
