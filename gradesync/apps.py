import redis
from django.apps import AppConfig

from utils.redis_conn import RedisClient


class GradesyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gradesync"

    def ready(self):
        redis_client = RedisClient()
        try:
            redis_client.get_connection.ping()
            print("Redis connection initialized successfully.")
        except redis.ConnectionError:
            print("Failed to connect to Redis. Please check your configuration.")
