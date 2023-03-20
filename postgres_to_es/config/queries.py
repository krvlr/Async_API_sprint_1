query_movies = """
SELECT
    fw.id AS id,
    COALESCE(fw.rating, 0) AS imdb_rating,
    COALESCE(array_agg(DISTINCT g.name) FILTER (WHERE g.name IS NOT NULL), '{{}}') AS genre,
    COALESCE(fw.title, '') AS title,
    COALESCE(fw.description, '') AS description,
    COALESCE(ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director'), '{{}}') AS director,
    COALESCE(ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor'), '{{}}') AS actors_names,
    COALESCE(ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer'), '{{}}') AS writers_names,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'actor'),
        '[]'
    ) AS actors,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'writer'),
        '[]'
    ) AS writers
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE LEAST(fw.modified, p.modified, g.modified) > '{}'
GROUP BY fw.id
"""


query_persons = """
WITH
--группируем роли актера по фильмам
agg AS (
SELECT
    p.id AS id,
    p.full_name AS full_name,
    pfw.film_work_id AS film_work_id,
    COALESCE(
        jsonb_agg(
            DISTINCT pfw.role
        ),
        '[]'
    ) AS roles
FROM content.person p
LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
LEFT JOIN content.film_work fw on fw.id = pfw.film_work_id
WHERE LEAST(fw.modified, p.modified) > '{}'
GROUP BY p.id, p.full_name, pfw.film_work_id, fw.modified
)

--собираем итоговую агрегацию
SELECT
    id,
    full_name,
    COALESCE(
        jsonb_agg(
            DISTINCT jsonb_build_object(
                'id', film_work_id,
                'roles', roles
            )
        ),
        '[]'
    ) AS films
FROM agg
GROUP BY id, full_name;
"""


query_genres = """
SELECT
    g.id AS id,
    g.name AS name,
    g.description AS description
FROM content.genre g
WHERE g.modified > '{}'
"""
