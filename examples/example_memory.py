from aiohttp import web

if __name__ == '__main__':
    import os
    import sys
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.join("..", os.path.abspath(__file__))))
    sys.path.insert(1, parent_dir)
    import aiohttp_cache
    
    __package__ = str("aiohttp_cache")
    
    from aiohttp_cache import cache, setup_cache
    
    @cache()
    async def example_1(request):
        return web.Response(text="Example")
    
    
    app = web.Application()
    
    app.router.add_route('GET', "/", example_1)

    setup_cache(app, cache_type="memory")
    
    web.run_app(app, host="127.0.0.1")
