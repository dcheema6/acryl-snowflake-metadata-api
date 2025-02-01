from typing import Callable, List

from cachetools import TTLCache

# Cache for 5 minutes since metadata doesn't change often
CACHE_TTL = 300

# Create separate caches for different endpoints
dbs_cache = TTLCache(maxsize=1, ttl=CACHE_TTL)
schemas_cache = TTLCache(maxsize=100, ttl=CACHE_TTL)
tables_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
columns_cache = TTLCache(maxsize=10000, ttl=CACHE_TTL)
summary_cache = TTLCache(maxsize=10000, ttl=CACHE_TTL)


class APICache:
    def __init__(self, cache: TTLCache):
        self.__cache__ = cache

    def __generate_key(self, keys: List[str]):
        return "|".join(str(key) for key in sorted(keys))

    def get(self, keys: List[str]):
        return self.__cache__.get(self.__generate_key(keys))

    def set(self, keys: List[str], value):
        self.__cache__[self.__generate_key(keys)] = value

    def contains(self, keys: List[str]):
        return self.__generate_key(keys) in self.__cache__

    def getCacheOrRefresh(self, keys: List[str], func: Callable):
        if self.contains(keys):
            # print("cache hit")
            return self.get(keys)
        else:
            # print("cache miss")
            value = func()
            self.set(keys, value)
            return value
