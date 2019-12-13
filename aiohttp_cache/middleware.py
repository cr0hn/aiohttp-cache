from aiohttp import web
from aiohttp.web_response import Response


@web.middleware
async def cache_middleware(request, handler):
    if getattr(handler, "cache_enable", False):
        #
        # Cache is disabled?
        #
        if getattr(handler, "cache_unless", False) is True:
            return await handler(request)

        cache_backend = request.app["cache"]

        key = await cache_backend.make_key(request)

        cached_response = await cache_backend.get(key)
        if cached_response:
            return Response(**cached_response)

        #
        # Generate cache
        #
        original_response = await handler(request)

        data = {
            "status": original_response.status,
            "headers": dict(original_response.headers),
            "body": original_response.body,
        }

        expires = getattr(handler, "cache_expires", 300)

        await cache_backend.set(key, data, expires)

        return original_response

    # Not cached
    return await handler(request)


__all__ = ("cache_middleware",)
