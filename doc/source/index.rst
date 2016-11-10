Welcome to aiohttp-cache documentation!
=======================================

*aiohttp-cache: A cache system for aiohttp server*

Project info
------------

- Project code: https://github.com/cr0hn/aiohttp-cache
- License: BSD
- Author: Daniel Garcia (cr0hn) - @ggdaniel

Installation
------------

Simple
++++++

Install aiohttp-cache is so easy:

.. code-block:: bash

    $ python3.5 -m pip install aiohttp-cache

.. note::

    **Remember that aiohttp-cache only runs in Python 3.5 and above**.

Supported backends
------------------

Currently there are two backends supported:

- Redis
- In Memory


Quick start
-----------

Use aiohttp-cache is so simple:

#. Decorate the functions that you want to cache
#. Initialize the aiohttp-cache

.. code-block:: python

    from aiohttp_cache import cache, setup_cache

    @cache()  # <-- DECORATED FUNCTION
    async def example_1(request):
        return web.Response(text="Example")


    app = web.Application()

    app.router.add_route('GET', "/", example_1)

    setup_cache(app)  # <-- INITIALIZED aiohttp-cache

    web.run_app(app, host="127.0.0.1")

Custom backend
--------------

When we initialize the aiohttp-cache we can choose the backend, setting the :samp:`cache_type`.

Redis
+++++

First, we must set into :samp:`setup_cache` the option: :samp:`cache_type="redis"`.

For configuring the Redis backend we need to fill the :samp:`RedisConfig` config object:

.. code-block:: python

    from aiohttp_cache import RedisConfig

    redis_config = RedisConfig(db=4,
                               key_prefix="my_example")

Available options are, following the definition:

.. code-block:: python

    class RedisConfig(_Config):

        def __init__(self,
                     host: str = 'localhost',
                     port: int = 6379,
                     db: int = 0,
                     password: str = None,
                     key_prefix: str = None):
        ...

Here the full example:

.. code-block:: python

    from aiohttp_cache import cache, setup_cache, RedisConfig

    @cache()
    async def example_1(request):
        return web.Response(text="Example")


    app = web.Application()

    app.router.add_route('GET', "/", example_1)

    redis_config = RedisConfig(db=4,
                               key_prefix="my_example")
    setup_cache(app, cache_type="redis")

    web.run_app(app, host="127.0.0.1")

In Memory
+++++++++

This kind of cache is very basic but could be useful in some cases. It store the cached information in memory.

The configuration is so simple. First we need to setup :samp:`cache_type="memory"`.

.. code-block:: python

    from aiohttp_cache import cache, setup_cache

    @cache()
    async def example_1(request):
        return web.Response(text="Example")


    app = web.Application()

    app.router.add_route('GET', "/", example_1)

    setup_cache(app)

    web.run_app(app, host="127.0.0.1")

.. note::

    This backend is not recommended for production

.. note::

    This is the **default backend** if not :samp:`cache_type` options is setted.

Per function configuration
--------------------------

We can set a grain fine configuration. We can specify this options per each end-point:

- Expire time (**in seconds**).
- Disable cache dynamically.

Expires
+++++++

If you want to setup a expire time for an end-point, we can parametrize the :samp:`@cache(...)` decorator:

.. code-block:: python

    @cache(expires=5)  # <--- TIME IN SECONDS!!
    async def example_1(request):
        return web.Response(text="Example")

.. note::

    If you not set the expires or **setup to 0** the cache will not expires.

Disable cache dynamically
+++++++++++++++++++++++++

Some times we need to disable the cache under certain situations, but not want to change all the function configuration, for example: when we're in a develop mode.

We can enable / disable the cache by setting :samp:`unless` value in the :samp:`@cache(...)` decorator:

.. code-block:: python

    @cache(unless=True)  # <-- Disable the Cache
    async def example_1(request):
        return web.Response(text="Example")

Or, a more realistic situation, in a development environment:

.. code-block:: python

    # main.py
    import os

    from aiohttp_cache import cache, setup_cache

    DEBUG = bool(os.environ.get("DEBUG", False))

    @cache(expires=5, unless=DEBUG)  # <-- Disable the Cache if we're in DEBUG mode
    async def example_1(request):
        return web.Response(text="Example")


    app = web.Application()

    app.router.add_route('GET', "/", example_1)

    setup_cache(app)

    web.run_app(app, host="127.0.0.1")

.. code-block:: bash

    $ export DEBUG="True"
    $ python3.5 main.py

Examples
--------

If you need more examples, there're some available in at folder: `aiohttp_cache/examples <https://github.com/cr0hn/aiohttp-cache/tree/master/examples>`_.

What's new?
-----------

You can read entire list in `CHANGELOG <https://github.com/cr0hn/aiohttp-cache/blob/master/CHANGELOG>`_ file.

Collaborate
-----------

You can to collaborate? Nice! You're wellcome :)

You can collaborate sending me a GitHub Pull Request with your proposal.

Acknowledgements
----------------

I want to thanks to `Flask-Cache <https://pythonhosted.org/Flask-Cache/>`_ author. I was take a lof ot ideas and some code from this project.
