import functools

from typing import Awaitable, Callable, Type, Union

from aiohttp import web
from aiohttp.abc import AbstractView, StreamResponse
from aiohttp.web_request import Request
from aiohttp.web_response import Response


_WebHandler = Callable[[Request], Awaitable[StreamResponse]]
HandlerType = Union[_WebHandler, Type[AbstractView]]


def get_original_handler(
    handler: Union[HandlerType, functools.partial]
) -> HandlerType:
    """Return the original handler object.

    In case the handler was provided as functools.partial or
    handler is hidden under chain of middlewares
    we need to extract the original handler object, in
    order to inspect if it is intended to be cached or not.
    """
    if hasattr(handler, "cache_enable"):
        return handler  # type: ignore
    elif hasattr(handler, "keywords"):
        try:
            return get_original_handler(
                handler.keywords["handler"]  # type: ignore
            )
        except KeyError:
            # handle the case when the handler type is functools.partial
            return handler.func  # type: ignore
    else:
        return handler  # type: ignore


@web.middleware
async def cache_middleware(
    request: web.Request, handler: HandlerType
) -> Union[Response, StreamResponse]:
    """Caching middleware.

    Identifies if the handler is intended to be cached.
    If yes, it caches the response using the caching
    backend and on the next call retrieve the response
    from the caching backend.
    """

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
