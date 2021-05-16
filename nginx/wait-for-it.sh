#!/bin/bash

API_HOST=${API_HOST:-127.0.0.1}
API_PORT=${API_PORT:-8888}

until curl -s ${API_HOST}:${API_PORT} >/dev/null; do
  echo >&2 "API is unavailable - sleeping"
  sleep 1
done

echo >&2 "API is up"

exit 0
