def retrieve_ratings(conn_ctx_manager):
    with conn_ctx_manager as cur:
        cur.execute("""
            select film_work_id, user_id, score from content.review_film_work;
            """)
        ratings = cur.fetchall()
        print(ratings[0])
        return ratings
