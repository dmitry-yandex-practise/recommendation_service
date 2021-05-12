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
select id, title, rating, type from content.film_work ORDER BY id;
""")
movies = cur.fetchall()
print(movies[0]["title"])

cur.execute("""
select film_work_id, user_id, score from content.review_film_work;
""")
ratings = cur.fetchall()
print(ratings[0])
