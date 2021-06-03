KEYS = ['user_id', 'film_work_id', 'score']


def name_filelds(keys, values):
    result = dict([(key, str(value),) for key, value in zip(keys, values)])
    return result

def retrieve_ratings(conn_ctx_manager):
    with conn_ctx_manager as cur:
        ratings = []
        query = "select user_id, film_work_id, score from ugc_data.review_film_work;"
        cur.execute(query)
        raw_result = cur.fetchall()
        for item in raw_result:
            temp_row = {
                'user_id': str(item[0]),
                'film_work_id': str(item[1]),
                'score': item[2]
            }
            ratings.append(temp_row)
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
