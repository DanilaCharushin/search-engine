#!/usr/bin/env sh

# This script runs in CI and optional in local runs of docker-compose

cd /backend || exit

chmod +x bin/wait.sh
sh -e bin/wait.sh postgres:5432 -- echo "postgres up"

/app/bin/python -m coverage run -m pytest "$@"
/app/bin/python -m coverage report
