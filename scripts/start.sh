#!/bin/bash

echo '======= RUNNING PIP INSTALL'
pip install --no-cache-dir -r requirements.txt
echo '======= MAKING MIGRATIONS'
python3 manage.py makemigrations
echo '======= RUNNING MIGRATIONS'
python3 manage.py migrate
echo '======= RUNNING SERVER'
python3 manage.py runserver 0.0.0.0:8000
