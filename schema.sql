-- Создаем отдельную схему для нашего контента, чтобы не перемешалось с сущностями Django
CREATE SCHEMA IF NOT EXISTS content;

-- Жанры, которые могут быть у кинопроизведений
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamp with time zone DEFAULT NOW(),
    updated_at timestamp with time zone DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content.users (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    updated_at timestamp with time zone DEFAULT NOW()
);

-- Убраны актеры, жанры, режиссеры и сценаристы, так как они находятся в отношении m2m с этой таблицей
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT not null,
    created_at timestamp with time zone DEFAULT NOW(),
    updated_at timestamp with time zone DEFAULT NOW()
);

-- Обобщение для актера, режиссера и сценариста
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE,
    created_at timestamp with time zone DEFAULT NOW(),
    updated_at timestamp with time zone DEFAULT NOW()
);

-- m2m таблица для связывания кинопроизведений с жанрами
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT NOW()
);

-- Обязательно проверяется уникальность жанра и кинопроизведения, чтобы не появлялось дублей
-- CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

CREATE TABLE IF NOT EXISTS content.review_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    user_id uuid NOT NULL,
    score int,
    is_like bool,
    created_at timestamp with time zone DEFAULT NOW()
);


-- m2m таблица для связывания кинопроизведений с участниками
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created_at timestamp with time zone DEFAULT NOW()
);

-- Обязательно проверяется уникальность кинопроизведения, человека и роли человека, чтобы не появлялось дублей
-- Один человек может быть сразу в нескольких ролях (например, сценарист и режиссер)
--  CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);
