import asyncio

import pytest
import yarl
from aiohttp import web
from aiohttp.test_utils import TestClient
from envparse import env

from aiohttp_cache import setup_cache, cache, RedisConfig

env.read_envfile("/aiohttp-cache/.env")

PAYLOAD = {"hello": "aiohttp_cache"}
WAIT_TIME = 2


@cache()
async def some_long_running_view(request: web.Request) -> web.Response:
    await asyncio.sleep(WAIT_TIME)
    payload = await request.json()
    return web.json_response(payload)


def build_application(cache_type="memory"):
    app = web.Application()
    if cache_type == "memory":
        setup_cache(app)
    elif cache_type == "redis":
        url = yarl.URL(env.str("CACHE_URL"))
        redis_config = RedisConfig(db=int(url.path[1:]), host=url.host, port=url.port)
        setup_cache(app, cache_type=cache_type, backend_config=redis_config)
    else:
        raise ValueError("cache_type should be `memory` or `redis`")
    app.router.add_post("/", some_long_running_view)
    return app


@pytest.fixture
def client_memory_cache(loop: asyncio.AbstractEventLoop, aiohttp_client) -> TestClient:
    client_: TestClient = loop.run_until_complete(
        aiohttp_client(build_application(cache_type="memory"))
    )

    # doing a first request to load it to the cache
    response = loop.run_until_complete(client_.post("/", json=PAYLOAD))

    assert response.status == 200
    return client_


@pytest.fixture
def client_redis_cache(loop: asyncio.AbstractEventLoop, aiohttp_client) -> TestClient:
    client_: TestClient = loop.run_until_complete(
        aiohttp_client(build_application(cache_type="redis"))
    )

    # doing a first request to load it to the cache
    response = loop.run_until_complete(client_.post("/", json=PAYLOAD))

    assert response.status == 200
    return client_
