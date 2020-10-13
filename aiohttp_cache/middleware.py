from typing import Any, TypeVar

from aiohttp import web


HandlerType = TypeVar("HandlerType", bound=Any)
T = TypeVar("T", bound=Any)


def get_original_handler(handler: HandlerType) -> HandlerType:
    if hasattr(handler, "cache_enable"):
        return handler
    elif hasattr(handler, "keywords"):
        return get_original_handler(handler.keywords["handler"])
    else:
        return handler


@web.middleware
async def cache_middleware(
    request: web.Request, handler: HandlerType
) -> web.Response:

    original_handler = get_original_handler(handler)

    if getattr(original_handler, "cache_enable", False):
        #
        # Cache is disabled?
        #
        if getattr(original_handler, "cache_unless", False) is True:
            return await handler(request)

        cache_backend = request.app["cache"]

        key = await cache_backend.make_key(request)

        cached_response = await cache_backend.get(key)
        if cached_response:
            return web.Response(**cached_response)

        #
        # Generate cache
        #
        original_response = await handler(request)

        data = {
            "status": original_response.status,
            "headers": dict(original_response.headers),
            "body": original_response.body,
        }

        expires = getattr(original_handler, "cache_expires", 300)

        await cache_backend.set(key, data, expires)

        return original_response

    # Not cached
    return await handler(request)


__all__ = ("cache_middleware",)
