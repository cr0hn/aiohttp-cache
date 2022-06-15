import asyncio

import pytest

from aiohttp import web
from aiohttp.test_utils import TestClient
from envparse import env

from aiohttp_cache import cache, setup_cache
from aiohttp_cache.backends import DEFAULT_KEY_PATTERN, AvailableKeys


PAYLOAD = {"hello": "aiohttp_cache"}
WAIT_TIME = 2


@cache()
async def some_long_running_view(request: web.Request) -> web.Response:
    await asyncio.sleep(WAIT_TIME)
    payload = await request.json()
    return web.json_response(payload)


def build_application(
    cache_type="memory",
    key_pattern=DEFAULT_KEY_PATTERN,
    encrypt_key=True,
) -> web.Application:
    app = web.Application()
    if cache_type == "memory":
        setup_cache(
            app,
            key_pattern=key_pattern,
            encrypt_key=encrypt_key,
        )
    elif cache_type == "redis":
        url = env.str("CACHE_URL", default="redis://localhost:6379/0")
        setup_cache(
            app,
            cache_type=cache_type,
            redis_url=url,
            key_pattern=key_pattern,
            encrypt_key=encrypt_key,
        )
    else:
        raise ValueError("cache_type should be `memory` or `redis`")
    app.router.add_post("/", some_long_running_view)
    return app


@pytest.fixture
def client_memory_cache(
    loop: asyncio.AbstractEventLoop, aiohttp_client
) -> TestClient:
    client_: TestClient = loop.run_until_complete(
        aiohttp_client(build_application(cache_type="memory"))
    )

    # doing a first request to load it to the cache
    response = loop.run_until_complete(client_.post("/", json=PAYLOAD))

    assert response.status == 200
    return client_


@pytest.fixture
def client_redis_cache(
    loop: asyncio.AbstractEventLoop, aiohttp_client
) -> TestClient:
    client_: TestClient = loop.run_until_complete(
        aiohttp_client(build_application(cache_type="redis"))
    )

    # doing a first request to load it to the cache
    response = loop.run_until_complete(client_.post("/", json=PAYLOAD))

    assert response.status == 200
    return client_


@pytest.fixture
def client_memory_cache_another_key(
    loop: asyncio.AbstractEventLoop,
    aiohttp_client,
) -> TestClient:
    client_: TestClient = loop.run_until_complete(
        aiohttp_client(
            build_application(
                cache_type="memory",
                key_pattern=(
                    AvailableKeys.method,
                    AvailableKeys.path,
                    AvailableKeys.json,
                ),
                encrypt_key=False,
            )
        )
    )

    # doing a first request to load it to the cache
    response = loop.run_until_complete(client_.post("/", json=PAYLOAD))

    assert response.status == 200
    return client_


@pytest.fixture
def client_redis_cache_another_key(
    loop: asyncio.AbstractEventLoop,
    aiohttp_client,
) -> TestClient:
    client_: TestClient = loop.run_until_complete(
        aiohttp_client(
            build_application(
                cache_type="redis",
                key_pattern=(
                    AvailableKeys.method,
                    AvailableKeys.path,
                    AvailableKeys.json,
                ),
                encrypt_key=False,
            )
        )
    )

    # doing a first request to load it to the cache
    response = loop.run_until_complete(client_.post("/", json=PAYLOAD))

    assert response.status == 200
    return client_
