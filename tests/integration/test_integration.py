import time

from tests.conftest import PAYLOAD


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
