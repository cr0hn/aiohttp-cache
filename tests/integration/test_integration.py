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
