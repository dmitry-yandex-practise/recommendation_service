def retrieve_movies_data(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
            select fw.id, fw.title, fw.type, fw.rating
            --ARRAY_AGG(DISTINCT G.NAME) AS GENRES,
            --ARRAY_AGG(DISTINCT P.FULL_NAME) AS PERSONS
            from content.film_work as fw
            --join content.genre_film_work as gfw on fw.id = gfw.film_work_id
            --join content.genre as g on gfw.genre_id = g.id
            --join content.person_film_work as pfw on fw.id = pfw.film_work_id
            --join content.person as p on pfw.person_id = p.id
            group BY fw.id;
            """)
        cur.execute(query)
        movies = cur.fetchall()
        print(movies[0])
        return movies
