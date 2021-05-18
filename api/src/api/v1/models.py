from typing import List, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field

from models.film import Film as FilmModel
from models.genre import Genre as GenreModel
from models.person import Person as PersonModel
from models.user import User as UserModel

"""
Здесь находятся модели, которые сериализются в ответ API
"""


class PaginatedList(BaseModel):
    page_number: int = Field(
        ..., description="Номер текущей страницы")
    count: int = Field(
        ..., description="Количество объектов на текущей странице")
    total_pages: int = Field(
        ..., description="Количество страниц в выдаче")


class Genre(BaseModel):
    id: UUID
    name: str = Field(
        ..., description="Имя жанра")

    @classmethod
    def from_model(cls, genre: GenreModel):
        return cls(
            id=genre.id,
            name=genre.name
        )


class PaginatedGenreList(PaginatedList):
    result: List[Genre]


class PersonShort(BaseModel):
    id: UUID
    name: str = Field(
        ..., description="Имя персоны")

    @classmethod
    def from_model(cls, person: PersonModel):
        return cls(
            id=person.id,
            name=person.name
        )


class Actor(PersonShort):
    pass


class Writer(PersonShort):
    pass


class Director(PersonShort):
    pass


class Person(PersonShort):
    actor: List[UUID] = Field(
        ..., description="Список id фильмов, в которых персона участвовала в качестве актёра")
    writer: List[UUID] = Field(
        ..., description="Список id фильмов, в которых персона участвовала в качестве сценариста")
    director: List[UUID] = Field(
        ..., description="Список id фильмов, в которых персона участвовала в качестве режиссёра")

    @classmethod
    def from_model(cls, person: PersonModel, person_films: Dict[str, List[FilmModel]]):
        return cls(
            id=person.id,
            name=person.name,
            actor=[film.id for film in person_films.get('actor', [])],
            writer=[film.id for film in person_films.get('writer', [])],
            director=[film.id for film in person_films.get('director', [])],
        )


class PaginatedPersonShortList(PaginatedList):
    result: List[PersonShort]


class PersonList(BaseModel):
    __root__: List[Person]


class GenreList(BaseModel):
    __root__: List[Genre]


class FilmShort(BaseModel):
    id: UUID
    title: str = Field(
        ..., description="Название фильма")
    imdb_rating: float = Field(
        ..., description="Рейтинг фильма")

    @classmethod
    def from_model(cls, film: FilmModel):
        return cls(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )


class Film(FilmShort):
    description: Optional[str] = Field(
        ..., description="Описание фильма")
    genres: List[Genre] = Field(
        ..., description="Список жанров фильма")
    actors: List[Actor] = Field(
        ..., description="Список актёров фильма")
    writers: List[Writer] = Field(
        ..., description="Список сценаристов фильма")
    directors: List[Director] = Field(
        ..., description="Список режиссёров фильма")

    @classmethod
    def from_model(cls, film: FilmModel):
        return cls(
            id=film.id,
            title=film.title,
            description=film.description,
            imdb_rating=film.imdb_rating,
            genres=[Genre(**genre.dict()) for genre in film.genres],
            actors=[Actor(**actor.dict()) for actor in film.actors],
            writers=[Writer(**writer.dict()) for writer in film.writers],
            directors=[Director(**director.dict()) for director in film.directors],
        )


class FilmShortList(BaseModel):
    __root__: List[FilmShort]


class PaginatedFilmShortList(PaginatedList):
    result: List[FilmShort]


class EventResp(BaseModel):
    success: bool


class User(BaseModel):
    id: UUID
    must_watch: List[FilmShort] = Field(
        ..., description='Список рекомендованных фильмов'
    )

    @classmethod
    def from_model(cls, user: UserModel):
        return cls(
            id=user.id,
            must_watch=[FilmShort(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
                        for film in user.must_watch],
        )
