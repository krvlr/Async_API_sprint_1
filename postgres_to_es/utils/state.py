"""Классы для хранения состояний"""

import abc
import json
import os
from typing import Any, Optional


class BaseStorage(abc.ABC):
    """
    Базовый класс для работы
    с постоянным хранилищем.
    """
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """
        Метод для сохранения
        состояния в постоянное хранилище.
        """
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """
        Метод для загрузки состояния
        локально из постоянного хранилища.
        """
        pass


class JsonFileStorage(BaseStorage):
    """
    Класс для работы
    с постоянным json-хранилищем.
    """
    def __init__(self, storage_path: Optional[str] = 'state.json'):
        self.storage_path = storage_path

    def save_state(self, state: dict) -> None:
        """
        Метод для сохранения состояния
        в постоянное хранилище.
        """
        with open(self.storage_path, 'w') as f:
            json.dump(state, f, separators=(',\n', ': '))

    def retrieve_state(self) -> dict:
        """
        Метод для загрузки состояния
        локально из постоянного хранилища.
        """
        if not os.path.isfile(self.storage_path):
            return {}

        with open(self.storage_path, 'r') as f:
            return json.load(f)


class State:
    """
    Класс для хранения состояния при работе с данными,
    чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    """
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """
        Метод для установления состояния
        по определённому ключу.
        """
        _storage = self.storage.retrieve_state()
        _storage[key] = value
        self.storage.save_state(_storage)

    def get_state(self, key: str, default: Any) -> Any:
        """
        Метод для получения
        состояния по определённому ключу.
        """
        return self.storage.retrieve_state().get(key, default)
