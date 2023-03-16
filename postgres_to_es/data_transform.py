from decorators import backoff

from pydantic import BaseModel


class DataTransform:
    @backoff()
    def validate_and_transform(self, model: BaseModel, objects: list[dict]) -> list[BaseModel]:
        return [model(**dict(obj)) for obj in objects]
