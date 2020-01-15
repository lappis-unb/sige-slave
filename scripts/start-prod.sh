#!/bin/bash

# Exporting all environment variables to use in crontab
env | sed 's/^\(.*\)$/ \1/g' > /root/env

echo '======= CHECKING FOR UNINSTALLED PKGs AND INSTALLING'
pip freeze || pip install -r requirements.txt

echo '======= MAKING MIGRATIONS'
python3 manage.py makemigrations

echo '======= RUNNING MIGRATIONS'
python3 manage.py migrate

echo '======= STARTING CRON'
cron

echo '======= RUNNING SERVER'
python3 manage.py runserver 0.0.0.0:8000
