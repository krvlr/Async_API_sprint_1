from decorators import backoff
from models import ESFilmworkData


class DataTransform:
    def _extract_names_and_ids_by_role(self, persons: list[dict], roles: list) -> dict:
        persons_data_by_role = {}
        for role in roles:
            names_and_ids = [
                {"id": field["person_id"], "name": field["person_name"]}
                for field in persons
                if field["person_role"] == role
            ]
            names = [name["name"] for name in names_and_ids]
            persons_data_by_role[role] = (names_and_ids, names)
        return persons_data_by_role

    @backoff()
    def validate_and_transform(self, movies: list[dict]) -> list[ESFilmworkData]:
        es_movies = []
        for film in movies:
            persons = self._extract_names_and_ids_by_role(
                film["persons"], ["director", "actor", "writer"]
            )
            es_filmwork = ESFilmworkData(
                id=film["id"],
                imdb_rating=film["rating"],
                genre=film["genres"],
                title=film["title"],
                description=film["description"],
                director=persons["director"][1],
                actors_names=persons["actor"][1],
                writers_names=persons["writer"][1],
                actors=persons["actor"][0],
                writers=persons["writer"][0],
            )
            es_movies.append(es_filmwork)
        return es_movies
