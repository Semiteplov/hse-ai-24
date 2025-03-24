import os

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0))
)

POPULAR_KEY = "popular_links"


def get_cached_url(short_code: str):
    return redis_client.get(short_code)


def set_cached_url(short_code: str, original_url: str):
    redis_client.set(short_code, original_url)


def delete_cached_url(short_code: str):
    redis_client.delete(short_code)


def increment_link_score(short_code: str):
    redis_client.zincrby(POPULAR_KEY, 1, short_code)


def get_top_links(n: int = 10):
    return redis_client.zrevrange(POPULAR_KEY, 0, n - 1, withscores=True)


def remove_from_popular(short_code: str):
    redis_client.zrem(POPULAR_KEY, short_code)
