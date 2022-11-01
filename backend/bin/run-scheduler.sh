#!/usr/bin/env sh

# This script runs only locally in docker-compose

cd /backend || exit

chmod +x bin/wait.sh
sh -e bin/wait.sh app:8000 -- echo "application up"

/app/bin/python manage.py runscheduler
