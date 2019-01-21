#!/bin/bash



pip install --no-cache-dir -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python manage.py runserver 0.0.0.0:8000
