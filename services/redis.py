from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import Redis
import redis

from data import config

redis_storage = RedisStorage(
    redis=Redis(
        host=config.FSM_HOST,
        port=config.FSM_PORT,
        password=config.FSM_PASSWORD,
        db=0,
    ),
    key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
)


class RedisClient:
    def __init__(self, host=config.FSM_HOST, port=config.FSM_PORT, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def set_state(self, key, state):
        self.client.set(key, state)

    def get_state(self, key):
        return self.client.get(key)

    def delete_state(self, key):
        self.client.delete(key)

    def get_all_states(self):
        keys = self.client.keys('*')
        return {key: self.client.get(key) for key in keys}
