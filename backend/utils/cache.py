"""
Redis Cache Utilities
Provides caching functionality for parking lot status
"""

# Lazy import to avoid circular dependency
def get_redis_client():
    """Get Redis client (lazy import to avoid circular dependency)"""
    from app import redis_client
    return redis_client

import json

CACHE_TTL = 300  # 5 minutes

def cache_lot_status(lot_id, lot_data):
    """Cache parking lot status in Redis"""
    try:
        r = get_redis_client()
        key = f"lot_status:{lot_id}"
        r.setex(
            key,
            CACHE_TTL,
            json.dumps(lot_data)
        )
    except Exception as e:
        print(f"Cache error: {e}")

def get_cached_lot_status(lot_id):
    """Get cached parking lot status from Redis"""
    try:
        r = get_redis_client()
        key = f"lot_status:{lot_id}"
        cached_data = r.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        print(f"Cache error: {e}")
        return None

def clear_lot_cache(lot_id):
    """Clear cache for a specific lot"""
    try:
        r = get_redis_client()
        key = f"lot_status:{lot_id}"
        r.delete(key)
    except Exception as e:
        print(f"Cache error: {e}")

def clear_all_cache():
    """Clear all lot status cache"""
    try:
        r = get_redis_client()
        keys = r.keys("lot_status:*")
        if keys:
            r.delete(*keys)
    except Exception as e:
        print(f"Cache error: {e}")

