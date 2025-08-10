import asyncio
from redis.asyncio import Redis, ConnectionPool
from typing import AsyncGenerator, Optional
import json
from functools import wraps
from typing import Callable, Awaitable
import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

class RedisSingleton:
    _client: Optional[Redis] = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_client(cls) -> Redis:
        if cls._client is None:
            async with cls._lock:
                # Double-checked locking to prevent race conditions
                if cls._client is None:
                    pool = ConnectionPool.from_url(
                        f"redis://{redis_host}:{redis_port}",
                        max_connections=20,
                        decode_responses=True
                    )
                    cls._client = Redis(connection_pool=pool)
        return cls._client

async def get_redis() -> AsyncGenerator[Redis, None]:
    client = await RedisSingleton.get_client()
    yield client

def redis_cache(key_builder: Callable[..., str], expire: int = 60):
    def decorator(func: Callable[..., Awaitable]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis: Redis = kwargs.get("redis")  # expect redis to be passed
            key = key_builder(*args, **kwargs)

            if redis is None:
                return await func(*args, **kwargs)

            # Try to get from Redis
            cached = await redis.get(key)
            if cached:
                return json.loads(cached)

            # Call original function
            result = await func(*args, **kwargs)

            # Cache the result
            await redis.set(key, json.dumps(result), ex=expire)
            return result

        return wrapper
    return decorator
