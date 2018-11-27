FROM python:3.6

RUN apt-get update

WORKDIR /smi-slave

COPY . /smi-slave

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_ENV="docker"

EXPOSE 5000
