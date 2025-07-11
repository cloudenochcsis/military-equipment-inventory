import json
import redis
import os
from datetime import timedelta
from functools import wraps
from fastapi import Request, Response
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union
from pydantic import BaseModel

# Get Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Create Redis connection
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0,
    socket_timeout=5,
    decode_responses=True
)

T = TypeVar('T', bound=BaseModel)

class CacheManager:
    """Redis cache manager for equipment inventory"""
    
    @staticmethod
    def set_cache(key: str, value: Any, expire_time_seconds: int) -> None:
        """Set cache value with expiration time"""
        try:
            if isinstance(value, BaseModel):
                value = value.dict()
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                value = [item.dict() for item in value]
                
            redis_client.set(key, json.dumps(value), ex=expire_time_seconds)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    @staticmethod
    def get_cache(key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            data = redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def delete_cache(key: str) -> None:
        """Delete cache value"""
        try:
            redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    @staticmethod
    def delete_pattern(pattern: str) -> None:
        """Delete all cache keys matching pattern"""
        try:
            for key in redis_client.scan_iter(match=pattern):
                redis_client.delete(key)
        except Exception as e:
            print(f"Cache pattern delete error: {e}")

# Cache decorators for FastAPI endpoints
def cache_response(expire_seconds: int, key_prefix: str):
    """Cache decorator for FastAPI endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name, prefix, and query parameters
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            
            if request:
                # Create a cache key from the path and query parameters
                path = request.url.path
                query_string = str(request.query_params)
                cache_key = f"{key_prefix}:{path}:{query_string}"
                
                # Try to get from cache
                cached_data = CacheManager.get_cache(cache_key)
                if cached_data:
                    return cached_data
            
            # Execute function if cache miss
            response = await func(*args, **kwargs)
            
            # Cache the response
            if request:
                CacheManager.set_cache(cache_key, response, expire_seconds)
            
            return response
        return wrapper
    return decorator

# Cache TTLs according to the caching strategy
CACHE_TTL = {
    "equipment_list": 60 * 5,  # 5 minutes
    "equipment_detail": 60 * 10,  # 10 minutes
    "search_results": 60 * 2,  # 2 minutes
    "statistics": 60 * 30,  # 30 minutes,
    "maintenance_schedule": 60 * 5, # 5 minutes
}
