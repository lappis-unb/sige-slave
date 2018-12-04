FROM python:3.6

WORKDIR /smi-slave

COPY . /smi-slave

ENV FLASK_ENV="docker"

ENV FLASK_DEBUG=1

ENV FLASK_APP=/smi-slave/src/app.py

RUN pip install --no-cache-dir -r requirements.txt

CMD flask run --host 0.0.0.0
