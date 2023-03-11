import abc
import json
from typing import Any, Optional

import redis
from decorators import backoff


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        pass


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    @backoff()
    def set_state(self, key: str, value: Any) -> None:
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        return self.storage.retrieve_state().get(key)


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = "./state.json"):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as state_file:
            json.dump(state, state_file)

    def retrieve_state(self) -> dict:
        try:
            with open(self.file_path, "r") as state_file:
                state = json.load(state_file)
        except json.JSONDecodeError:
            state = {}
        return state


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: redis.Redis):
        self.redis_adapter = redis_adapter

    @backoff()
    def save_state(self, state: dict) -> None:
        self.redis_adapter.hset("state", mapping=state)

    @backoff()
    def retrieve_state(self) -> dict:
        return self.redis_adapter.hgetall("state")
