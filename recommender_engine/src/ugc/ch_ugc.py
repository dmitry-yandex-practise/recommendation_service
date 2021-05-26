def retrieve_ratings(conn_ctx_manager):
    with conn_ctx_manager as cur:
        query = cur.mogrify("""
            select user_id, film_work_id, score from ugc_data.review_film_work;
            """)
        cur.execute(query)
        ratings = cur.fetchall()
        print(ratings[0])
        return ratings


def retrieve_top_movies(conn_ctx_manager, k: int):
    with conn_ctx_manager as cur:
        query = cur.mogrify(f"""
            SELECT topK({k})(DISTINCT film_work_id) AS res
            FROM ugc_data.movie_view;
            """)
        cur.execute(query)
        top = cur.fetchall()
        print(top[0])
        return top
