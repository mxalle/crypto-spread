import redis

REDIS_URL = "redis://127.0.0.1:6379"

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

