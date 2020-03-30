#!/bin/bash

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

function_postgres_ready() {
python << END
import socket
import time
import os

port = int(os.environ["POSTGRES_PORT"])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(('slave-db', port))
s.close()
END
}

echo '======= CHECKING FOR UNINSTALLED PKGs AND INSTALLING'
pip freeze || pip install -r requirements.txt

until function_postgres_ready; do
  >&2 echo "======= POSTGRES IS UNAVAILABLE, WAITING"
  sleep 1
done
echo "======= POSTGRES IS UP, CONNECTING"

echo '======= MAKING MIGRATIONS'
python3 manage.py makemigrations

echo '======= RUNNING MIGRATIONS'
python3 manage.py migrate

# echo '======= RUNNING SEED'
# python3 seed_db.py

echo '======= STARTING CRON'
cron

echo '======= RUNNING SERVER'
python3 manage.py runserver 0.0.0.0:8000
