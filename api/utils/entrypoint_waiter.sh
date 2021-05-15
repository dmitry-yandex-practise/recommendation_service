#!/bin/bash

REDIS_HOST=${REDIS_HOST:-127.0.0.1}
REDIS_PORT=${REDIS_PORT:-6379}
ELASTIC_HOST=${ELASTIC_HOST:-127.0.0.1}
ELASTIC_PORT=${ELASTIC_PORT:-9200}

while :; do
  ping=$({ exec 3<>/dev/tcp/${REDIS_HOST}/${REDIS_PORT} && echo -e "PING\r\n" >&3 && head -c 5 <&3; } 2>&1)
  if [ "$ping" = "+PONG" ]; then
    break
  else
    echo echo "Redis is unavailable - sleeping"
    sleep 1
  fi
done

echo >&2 "Redis is up"

until curl -s ${ELASTIC_HOST}:${ELASTIC_PORT} >/dev/null; do
  echo >&2 "ElasticSearch is unavailable - sleeping"
  sleep 3
done

echo >&2 "ElasticSearch is up"

exec "$@"
