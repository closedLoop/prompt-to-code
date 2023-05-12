#!/bin/bash
# launch.sh
set -e

docker compose down --remove-orphans
docker compose rm -f

# Remove all volumes
docker volume ls --filter name=prompt* --format 'json {{.Name}}'  | grep prompt | xargs docker volume rm
