FROM python:3.6

RUN apt update && \
    apt install -y libpq-dev \
                       cron

WORKDIR /smi-slave

COPY . /smi-slave

# Setting cron
COPY crons/cronjob /etc/cron.d/smi-cron

RUN chmod 0644 /etc/cron.d/smi-cron

RUN touch /var/log/cron.log

RUN /usr/bin/crontab /etc/cron.d/smi-cron

RUN pip install --no-cache-dir -r requirements.txt
