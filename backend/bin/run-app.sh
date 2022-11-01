#!/usr/bin/env sh

# This script runs only locally in docker-compose

cd /backend || exit

chmod +x bin/wait.sh
sh -e bin/wait.sh postgres:5432 -- echo "postgres up"
sh -e bin/wait.sh redis:6379 -- echo "redis up"

/app/bin/python manage.py collectstatic --noinput &
/app/bin/python manage.py migrate &&
wait

# Get admin user and create him if no one found
cat <<EOF | /app/bin/python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username="admin").exists() or User.objects.create_superuser("admin", "admin@admin.admin", "admin")
EOF

/app/bin/gunicorn app.wsgi --workers=2 --bind 0.0.0.0:8000 --reload --access-logfile -
