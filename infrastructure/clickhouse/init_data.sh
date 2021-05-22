#!/bin/bash

clickhouse-client --format_csv_delimiter="," --query="INSERT INTO ugc_data.review_film_work FORMAT CSV" < /tmp/init_data/pg_review_data_all.csv
