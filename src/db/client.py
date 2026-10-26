import os
from functools import lru_cache

from psycopg_pool import ConnectionPool


@lru_cache(maxsize=1)
def get_pool() -> ConnectionPool:
    url = os.environ.get("DB_URL")
    if not url:
        raise RuntimeError("DB_URL is not set")
    return ConnectionPool(url, min_size=1, max_size=int(os.environ.get("DB_POOL_MAX", "10")), open=True)
