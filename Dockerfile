FROM python:3.6

RUN apt-get update && \
    apt-get install -y postgresql \
                       postgresql-client \
                       libpq-dev

WORKDIR /smi-slave

COPY . /smi-slave

RUN pip install --no-cache-dir -r requirements.txt
