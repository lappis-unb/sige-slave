FROM python:3.6

RUN apt-get update && \
    apt-get install -y postgresql \
                       postgresql-client \
                       libpq-dev

WORKDIR /smi-slave

COPY . /smi-slave

RUN echo 'SEEDING DB'

RUN python3 manage.py loaddata data_reader/fixtures/initial_data.json

RUN pip install --no-cache-dir -r requirements.txt
