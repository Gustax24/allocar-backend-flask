import redis
from flask import current_app

class RedisCache:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        url = app.config["REDIS_URL"]
        self.client = redis.Redis.from_url(url, decode_responses=True)

cache = RedisCache()
