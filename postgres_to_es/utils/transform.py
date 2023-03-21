"""Функции и классы для преобразования данных из формата Postgres в формат, пригодный для Elasticsearch."""


class DataTransform:
    """
    Класс для преобразования
    данных выгруженных из PostgreSQL,
    для их загрузки в Elasticsearch.
    """

    def __init__(self, transform_model):
        self._transform_model = transform_model

    def transform(self, row):
        """
        Метод для преобразования строки
        к формату Elasticsearch.
        """
        doc = {
            '_id': row['id'],
            '_source': self._transform_model.custom_validate(**row).dict(),
        }
        return doc

    def get_batch_transformer(self, rows):
        """
        Метод для преобразования батча
        к формату Elasticsearch.
        """
        for row in rows:
            yield self.transform(row)
