FROM python:3.6

RUN apt-get update

WORKDIR /smi-slave

ADD . /smi-slave

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
