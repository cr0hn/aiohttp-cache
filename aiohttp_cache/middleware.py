from aiohttp.web_response import Response

async def cache_middleware(app, handler):
    async def middleware_handler(request):
        _handler = request.match_info.handler
        
        if getattr(_handler, "cache_enable", False):
            #
            # Cache is disabled?
            #
            if getattr(_handler, "cache_unless", False) is True:
                return await _handler(request)
            
            cache_backend = app["cache"]
            
            key = await cache_backend.make_key(request)

            cached_response = await cache_backend.get(key)
            if cached_response:
                return Response(**cached_response)
            
            #
            # Generate cache
            #
            original_response = await _handler(request)
            
            data = dict(status=original_response.status,
                        headers=dict(original_response.headers),
                        body=original_response.body)

            expires = getattr(_handler, "cache_expires", 300)
            
            await cache_backend.set(key, data, expires)
            
            return original_response
        
        # Not cached
        return await _handler(request)
    
    return middleware_handler


__all__ = ("cache_middleware", )
