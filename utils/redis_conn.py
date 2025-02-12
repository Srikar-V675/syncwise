import json
import uuid

import redis
from django.conf import settings


class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,  # Optional: Decode strings automatically
            )
        return cls._instance

    @property
    def get_connection(self):
        return self._instance.connection


def init_scraping_redis_key(total: int):
    name = str(uuid.uuid4())

    redis_client = RedisClient().get_connection
    mapping = {
        "progress": 0,
        "total": total,
        "errors": json.dumps([]),
        "stop": "",
    }
    redis_client.hset(name=name, mapping=mapping)
    redis_client.expire(name=name, time=10800)  # expiry in 3 hrs

    return name


def incr_scraping_progress(name: str):
    redis_client = RedisClient().get_connection
    redis_client.hincrby(name=name, key="progress", amount=1)


def log_scraping_errors(name: str, errors: list):
    redis_client = RedisClient().get_connection
    redis_client.hset(name=name, key="errors", value=json.dumps(errors))


def get_scraping_info(name: str):
    redis_client = RedisClient().get_connection
    return redis_client.hgetall(name=name)


def change_stop_field(name: str, value: str):
    redis_client = RedisClient().get_connection
    redis_client.hset(name=name, key="stop", value=value)
