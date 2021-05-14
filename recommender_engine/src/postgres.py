import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host="localhost",
    database="movies_database",
    user="postgres",
    password="pass"
)

cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("""
select fw.id, fw.title, fw.type
--ARRAY_AGG(DISTINCT G.NAME) AS GENRES,
--ARRAY_AGG(DISTINCT P.FULL_NAME) AS PERSONS
from content.film_work as fw
--join content.genre_film_work as gfw on fw.id = gfw.film_work_id
--join content.genre as g on gfw.genre_id = g.id
--join content.person_film_work as pfw on fw.id = pfw.film_work_id
--join content.person as p on pfw.person_id = p.id
group BY fw.id;
""")
movies = cur.fetchall()
print(movies[0])

cur.execute("""
select film_work_id, user_id, score from content.review_film_work;
""")
ratings = cur.fetchall()
print(ratings[0])

cur.execute("""
select id, name from content.users;
""")
users = cur.fetchall()
print(users[0])
