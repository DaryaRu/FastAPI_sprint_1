"""Transforms PostgreSQL into ETL models."""

from models import FilmWork, Person


def build_film_work(
    row: dict,
    genres: list[str],
    persons: dict[str, list[Person]],
) -> FilmWork:
    """Build a FilmWork document."""
    directors = list(persons["directors"])
    actors = list(persons["actors"])
    writers = list(persons["writers"])
    result = FilmWork(
        id=row["id"],
        imdb_rating=row.get("imdb_rating"),
        genres=genres,
        title=row["title"],
        description=row.get("description"),
        directors_names=[person.name for person in directors],
        actors_names=[person.name for person in actors],
        writers_names=[person.name for person in writers],
        directors=directors,
        actors=actors,
        writers=writers,
    )
    return result


def group_genres_by_film(rows: list[dict]) -> dict:
    """Group genre names by film_work_id."""
    grouped_genres: dict = {}
    for row in rows:
        film_work_id = row["film_work_id"]
        grouped_genres.setdefault(film_work_id, [])
        genre_name = row["name"]
        if genre_name not in grouped_genres[film_work_id]:
            grouped_genres[film_work_id].append(genre_name)
    return grouped_genres


def group_persons_by_film(rows: list[dict]) -> dict:
    """Group persons by film_work_id and group them by roles."""
    grouped_persons: dict = {}
    for row in rows:
        film_work_id = row["film_work_id"]
        film_persons = grouped_persons.setdefault(
            film_work_id,
            {
                "directors": [],
                "actors": [],
                "writers": [],
            },
        )
        role = row["role"]
        person = Person(id=row["id"], name=row["full_name"])
        if role == "director":
            target_key = "directors"
        elif role == "actor":
            target_key = "actors"
        else:
            target_key = "writers"
        if person.id not in {item.id for item in film_persons[target_key]}:
            film_persons[target_key].append(person)
    return grouped_persons
