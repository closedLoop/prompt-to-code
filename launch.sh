#!/bin/bash
# launch.sh
set -e

docker compose down --remove-orphans
docker compose rm -f

# CHECK FOR NETWORK and create if necessary
NETWORK_EXISTS=$(docker network ls --filter name=taskforce --no-trunc -q)

if [ -z "$NETWORK_EXISTS" ]; then
  echo "Network 'taskforce' does not exist. Creating..."
  docker network create taskforce
else
  echo "Network 'taskforce' already exists. Skipping creation..."
fi

# Load the .env file
if [ -f .env ]
then
  while IFS= read -r line
  do
    if [[ "$line" =~ ^[a-zA-Z_][a-zA-Z_0-9]*= ]]; then
      name=$(echo $line | cut -d '=' -f 1)
      value=$(echo $line | cut -d '=' -f 2- | sed -e 's/^"//' -e 's/"$//')
      export $name="$value"
    fi
  done < .env
fi

# Launch
echo "Launching containers..."
docker compose up -d

DB_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' taskforce-db)"

./wait-for-it.sh "$DB_IP" 5432 echo "Database is up"

# UPDATE ENVIRONMENT VARIABLES
DB_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' taskforce-db)"
sed -i 's|DATABASE_URL=.*|DATABASE_URL='"$DB_IP"':5432|' .env


# Load the .env file
if [ -f .env ]
then
  while IFS= read -r line
  do
    if [[ "$line" =~ ^[a-zA-Z_][a-zA-Z_0-9]*= ]]; then
      name=$(echo $line | cut -d '=' -f 1)
      value=$(echo $line | cut -d '=' -f 2- | sed -e 's/^"//' -e 's/"$//')
      export $name="$value"
    fi
  done < .env
fi

echo "Updating database schema"
python -m prisma db push

echo "Seeding database - not implemented yet"

echo "To launch Prisma Studio run"
echo "    $ prisma studio"

echo "To launch the backend run"

# CHECK FOR PREFECT PROFILE and create if necessary
PROFILE_EXISTS=$(prefect profile ls | grep taskforce)

if [ -z "$PROFILE_EXISTS" ]; then
  echo "Prefect profile 'taskforce' does not exist. Creating..."
  prefect profile create taskforce
else
  echo "Prefect profile 'taskforce' already exists. Skipping creation..."
fi

API_SERVER_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' taskforce-server)"
prefect --profile taskforce config set PREFECT_API_URL="http://$API_SERVER_IP:4200/api"
prefect profile use taskforce

docker compose logs -f --tail 1000
