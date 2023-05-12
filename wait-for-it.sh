#!/bin/sh
# wait-for-it.sh

set -e

host="$1"
shift
port="$1"
shift

until nc -z "$host" "$port" 2>/dev/null; do
  echo "Waiting for $host:$port..."
  sleep 1
done

echo "$host:$port is available"

exec "$@"
