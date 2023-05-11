

# To launch

<!-- docker network create taskforce -->
docker-compose up -d

# After it loads then


## Configuring the database

get ipaddress of database

    docker inspect --format='{{range .NetworkSettings.Networks}}{{println .IPAddress}}{{end}}'

    set DATABASE_URL="172.25.0.5:5432"
    python -m prisma db push

### Launch prisma studio

    python -m prisma studio
