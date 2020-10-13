from typing import Any, TypeVar


T = TypeVar("T", bound=Any)


class cache(object):  # noqa
    def __init__(self, expires: int = 3600, unless: bool = False):
        self.expires = expires
        self.unless = unless

    def __call__(self, f: T) -> T:
        f.cache_enable = True
        f.cache_expires = self.expires
        f.cache_unless = self.unless

        return f


__all__ = ("cache",)
