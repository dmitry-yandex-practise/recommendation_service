#!/bin/bash

clickhouse-client --format_csv_delimiter="," --query="INSERT INTO ugc_data.review_film_work FORMAT CSV" < /tmp/init_data/pg_review_data_all.csv
clickhouse-client --format_csv_delimiter="," --query="INSERT INTO ugc_data.movie_view FORMAT CSV" < /tmp/init_data/film_work_views.csv
clickhouse-client --format_csv_delimiter="," --query="INSERT INTO ugc_data.person_view FORMAT CSV" < /tmp/init_data/person_views.csv
