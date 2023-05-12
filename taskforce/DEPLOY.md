

# To launch

<!-- docker network create taskforce -->
docker-compose up -d

# After it loads then


## Configuring the database

get ipaddress of database

    export DATABASE_URL="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' taskforce-db):5432"

    DB_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' taskforce-db)"
    sed -i 's|DATABASE_URL=localhost:5432|DATABASE_URL='"$DB_IP"':5432|' .env


    DB_IP="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' taskforce-db)"
    sed -i 's|DATABASE_URL=localhost:5432|DATABASE_URL=postgresql://username:password@'"$DB_IP"':5432/database_name|' .env

    set DATABASE_URL="172.25.0.2:5432"
    python -m prisma db push

### Launch prisma studio

    python -m prisma studio
