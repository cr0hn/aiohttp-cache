import asyncio
import enum
import pickle  # nosec
import time

from hashlib import sha256
from typing import Any, Dict, Optional, Tuple, TypeVar

import aiohttp.web
import aioredis


T = TypeVar("T", bound=Any)


class AvailableKeys(enum.Enum):
    """Available keys to construct the index key for cache entry."""

    method = "method"
    host = "host"
    path = "path"
    postdata = "postdata"
    ctype = "ctype"
    json = "json"


DEFAULT_KEY_PATTERN = (
    AvailableKeys.method,
    AvailableKeys.host,
    AvailableKeys.path,
    AvailableKeys.postdata,
    AvailableKeys.ctype,
)


class BaseCache(object):
    def __init__(
        self,
        expiration: int = 300,
        key_pattern: Tuple[AvailableKeys, ...] = DEFAULT_KEY_PATTERN,
        encrypt_key: bool = True,
    ):
        self.encrypt_key = encrypt_key
        self.expiration = expiration
        self.key_pattern = key_pattern

    async def get(self, key: str) -> Optional[T]:
        raise NotImplementedError()

    async def delete(self, key: str) -> None:
        raise NotImplementedError()

    async def has(self, key: str) -> bool:
        raise NotImplementedError()

    async def clear(self) -> None:
        raise NotImplementedError()

    async def set(self, key: str, value: dict, expires: int = 3000) -> None:
        raise NotImplementedError()

    async def make_key(self, request: aiohttp.web.Request) -> str:
        k = AvailableKeys
        known_keys = {
            k.method: request.method,
            k.path: request.rel_url.path_qs,
            k.host: request.url.host,
            k.postdata: "".join(await request.post()),
            k.ctype: request.content_type,
            k.json: await request.text(),
        }

        if not all(key in k for key in known_keys):
            raise AssertionError()
        key = "#".join(known_keys[key] for key in self.key_pattern)

        if self.encrypt_key:
            key = sha256(key.encode()).hexdigest()

        return key

    def _calculate_expires(self, expires: int) -> int:
        return self.expiration if expires is None or expires < 0 else expires


class _Config:
    def __init__(self, expiration: int = 300):
        self.expiration = expiration


# --------------------------------------------------------------------------
# REDIS BACKEND
# --------------------------------------------------------------------------
class RedisConfig(_Config):
    """Redis configuration as a caching backend."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        key_prefix: str = None,
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.key_prefix = key_prefix or ""

        super(RedisConfig, self).__init__()


class RedisCache(BaseCache):
    """Redis Cache."""

    def __init__(
        self,
        config: RedisConfig,
        *,
        loop: asyncio.BaseEventLoop = None,
        expiration: int = 300,
        key_pattern: Tuple[AvailableKeys, ...] = DEFAULT_KEY_PATTERN,
        encrypt_key: bool = True,
    ):
        BaseCache.__init__(self, config.expiration)
        _loop = loop or asyncio.get_event_loop()

        self._redis_pool = _loop.run_until_complete(
            aioredis.create_pool(
                (config.host, config.port),
                db=config.db,
                password=config.password,
            )
        )
        self.key_prefix = config.key_prefix
        super().__init__(
            expiration=expiration,
            key_pattern=key_pattern,
            encrypt_key=encrypt_key,
        )

    @staticmethod
    def dump_object(value: dict) -> bytes:
        """Serialize the object into bytes."""
        t = type(value)
        if t in (int,):
            return str(value).encode("ascii")
        return b"!" + pickle.dumps(value)

    def load_object(self, value: Optional[T] = None) -> Optional[T]:
        """Deserialize the object.

        This might be called with None.
        """

        if value is None:
            return None
        if value.startswith(b"!"):
            try:
                return pickle.loads(value[1:])  # nosec
            except pickle.PickleError:
                return None
        try:
            return int(value)  # type: ignore
        except ValueError:
            # before 0.8 we did not have serialization.  Still support that.
            return value

    async def get(self, key: str) -> Optional[T]:
        async with self._redis_pool.get() as redis:
            redis_value = await redis.execute("GET", self.key_prefix + key)

            return self.load_object(redis_value)

    async def set(
        self, key: str, value: dict, expires: int = 3000
    ) -> None:  # noqa
        dump = self.dump_object(value)

        _expires = self._calculate_expires(expires)

        if _expires == 0:
            async with self._redis_pool.get() as redis:
                await redis.execute("SET", self.key_prefix + key, dump)
        else:
            async with self._redis_pool.get() as redis:
                await redis.execute(
                    "SETEX", self.key_prefix + key, _expires, dump
                )

    async def delete(self, key: str) -> None:
        async with self._redis_pool.get() as redis:
            await redis.execute("DEL", self.key_prefix + key)

    async def has(self, key: str) -> bool:
        async with self._redis_pool.get() as redis:
            return await redis.execute("EXISTS", self.key_prefix + key)

    async def clear(self) -> None:
        async with self._redis_pool.get() as redis:
            if self.key_prefix:
                keys = await redis.execute("KEYS", self.key_prefix + "*")
                if keys:
                    await redis.execute("DEL", *keys)
            else:
                await redis.flushdb()


# --------------------------------------------------------------------------
# MEMORY BACKEND
# --------------------------------------------------------------------------
class MemoryCache(BaseCache):
    """Memory Cache class."""

    def __init__(
        self,
        *,
        expiration: int = 300,
        key_pattern: Tuple[AvailableKeys, ...] = DEFAULT_KEY_PATTERN,
        encrypt_key: bool = True,
    ):
        super().__init__(
            expiration=expiration,
            key_pattern=key_pattern,
            encrypt_key=encrypt_key,
        )

        #
        # Cache format:
        # (cached object, expire date)
        #
        self._cache: Dict[str, Tuple[dict, int]] = {}

    async def get(self, key: str) -> Optional[T]:
        # Update the keys
        self._update_expiration_key(key)

        try:
            cached = self._cache[key]

            return cached[0]  # type: ignore
        except KeyError:
            return None

    async def set(
        self, key: str, value: dict, expires: int = 3000
    ) -> None:  # noqa
        _expires = self._calculate_expires(expires)

        self._cache[key] = (value, int(time.time()) + _expires)

    async def has(self, key: str) -> bool:
        # Update the keys
        self._update_expiration_key(key)

        return key in self._cache

    async def delete(self, key: str) -> None:
        # Update the keys
        self._update_expiration_key(key)

        try:
            del self._cache[key]
        except KeyError:
            pass

    async def clear(self) -> None:
        self._cache = {}

    def _update_expiration_key(self, key: str) -> None:
        try:
            expiration = self._cache[key][1]

            if expiration < int(time.time()):
                del self._cache[key]
        except KeyError:
            pass


__all__ = (
    "MemoryCache",
    "RedisCache",
    "RedisConfig",
    "AvailableKeys",
    "DEFAULT_KEY_PATTERN",
)
