import pickle
from abc import abstractmethod, ABCMeta


class CacheSerializer(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def serialize(data):
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data):
        pass


class PickleCacheSerializer(CacheSerializer):
    @staticmethod
    def serialize(data):
        return pickle.dumps(data)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)
