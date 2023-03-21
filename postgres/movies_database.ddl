BEGIN;

CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid DEFAULT gen_random_uuid () PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid DEFAULT gen_random_uuid () PRIMARY KEY,
    name text NOT NULL,
    description text,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    modified timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid DEFAULT gen_random_uuid () PRIMARY KEY,
    genre_id uuid NOT NULL REFERENCES content.genre (id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid DEFAULT gen_random_uuid () PRIMARY KEY,
    full_name text NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    modified timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL

);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid DEFAULT gen_random_uuid () PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES content.person (id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    created timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id);

COMMIT;