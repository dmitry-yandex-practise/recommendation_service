def retrieve_ratings(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
            select user_id, film_work_id, score from content.review_film_work;
            """)
        cur.execute(query)
        ratings = cur.fetchall()
        print(ratings[0])
        return ratings
