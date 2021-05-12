movie_field_names = ('rotten_tomatoes_link', 'movie_title', 'movie_info',
               'critics_consensus', 'content_rating', 'genres',
               'directors', 'authors', 'actors', 'original_release_date',
               'streaming_release_date', 'runtime','production_company',
               'tomatometer_status','tomatometer_rating','tomatometer_count',
               'audience_status', 'audience_rating', 'audience_count',
               'tomatometer_top_critics_count', 'tomatometer_fresh_critics_count',
               'tomatometer_rotten_critics_count')

review_field_names = ('rotten_tomatoes_link', 'critic_name', 'top_critic',
                      'publisher_name', 'review_type', 'review_score',
                      'review_date', 'review_content')

def name_filelds(keys, values):
    result = dict([(key, value,) for key, value in zip(keys, values)])
    return result
