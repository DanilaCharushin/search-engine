#!/usr/bin/env sh

# This script runs only locally in docker-compose

cd /backend || exit

chmod +x bin/wait.sh
sh -e bin/wait.sh postgres:5432 -- echo "postgres up"
sh -e bin/wait.sh redis:6379 -- echo "redis up"

/app/bin/python manage.py rundramatiq --reload -p 15 -t 4
