import functools
import logging
import time

from collections.abc import Callable
from typing import Dict

from aiohttp import web

from aiohttp_cache import cache, setup_cache
from tests.conftest import PAYLOAD


logger = logging.getLogger(__name__)


async def test_memory_cache(client_memory_cache):
    # check if cache really exists
    assert client_memory_cache.app["cache"]

    # check if the response is coming from cache (quick)
    tic = time.monotonic()
    resp = await client_memory_cache.post("/", json=PAYLOAD)
    assert resp.status == 200
    assert await resp.json() == PAYLOAD
    assert (time.monotonic() - tic) < 0.1


async def test_redis_cache(client_redis_cache):
    # check if cache really exists
    assert client_redis_cache.app["cache"]

    # check if the response is coming from cache (quick)
    tic = time.monotonic()
    resp = await client_redis_cache.post("/", json=PAYLOAD)
    assert resp.status == 200
    assert await resp.json() == PAYLOAD
    assert (time.monotonic() - tic) < 0.1


async def test_key_patterns_memory(client_memory_cache_another_key):
    resp = await client_memory_cache_another_key.post("/", json=PAYLOAD)
    assert resp.status == 200
    cache = client_memory_cache_another_key.app["cache"]
    res = await cache.get(r'POST#/#{"hello": "aiohttp_cache"}')
    assert res == {
        "status": 200,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": b'{"hello": "aiohttp_cache"}',
    }


async def test_key_patterns_redis(client_redis_cache_another_key):
    resp = await client_redis_cache_another_key.post("/", json=PAYLOAD)
    assert resp.status == 200
    cache = client_redis_cache_another_key.app["cache"]
    res = await cache.get(r'POST#/#{"hello": "aiohttp_cache"}')
    assert res == {
        "status": 200,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": b'{"hello": "aiohttp_cache"}',
    }


async def test_various_handlers_type(aiohttp_client, caplog):
    @cache()
    async def handler_a(request: web.Request) -> web.Response:
        text = await request.text()
        return web.Response(text=f"Hello from handler a. Request was: {text}")

    @cache()
    async def handler_b(request: web.Request, settings: Dict) -> web.Response:
        text = await request.text()
        return web.Response(text=f"Hello from handler a. Request was: {text}")

    @web.middleware
    async def middleware_1(request: web.Request, handler: Callable):
        logger.info("Entering middleware 1")
        resp: web.Response = await handler(request)
        logger.info("Exiting middleware 1")
        return web.Response(text=resp.text + " -- Added by middleware 1")

    @web.middleware
    async def middleware_2(request: web.Request, handler: Callable):
        logger.info("Entering middleware 2")
        resp: web.Response = await handler(request)
        logger.info("Exiting middleware 2")
        return web.Response(text=resp.text + " -- Added by middleware 2")

    app = web.Application()
    app.router.add_get("/a", handler_a)
    app.router.add_get(
        "/b", functools.partial(handler_b, settings={"some": "settings"})
    )
    setup_cache(app)
    app.middlewares.append(middleware_1)
    app.middlewares.append(middleware_2)

    client = await aiohttp_client(app)
    await client.get("/a")
    await client.get("/a")
    await client.get("/b")
    await client.get("/b")
    # making sure that for cached requests, the middleware wasn't called
    # otherwise more messages will take place
    assert len(caplog.messages) == 13
