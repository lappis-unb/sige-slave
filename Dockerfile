FROM python:3.10.9-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    logrotate \
    libpq-dev \
    cron \
    tzdata \
    locales

RUN sed -i 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen pt_BR.UTF-8

ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR
ENV LC_ALL pt_BR.UTF-8

RUN dpkg-reconfigure --frontend noninteractive locales

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

WORKDIR /smi-slave

COPY . /smi-slave

# Config lograte
RUN mkdir -p /etc/logrotate.d && \
    touch /smi-slave/logs/cronjobs_execution.log && \
    echo "/smi-slave/logs/cronjobs_execution.log {" > /etc/logrotate.d/smi_slave && \
    echo "  size 100M" >> /etc/logrotate.d/smi_slave && \
    echo "  daily" >> /etc/logrotate.d/smi_slave && \
    echo "  missingok" >> /etc/logrotate.d/smi_slave && \
    echo "  rotate 7" >> /etc/logrotate.d/smi_slave && \
    echo "  compress" >> /etc/logrotate.d/smi_slave && \
    echo "  delaycompress" >> /etc/logrotate.d/smi_slave && \
    echo "  notifempty" >> /etc/logrotate.d/smi_slave && \
    echo "  create 0644 root root" >> /etc/logrotate.d/smi_slave && \
    echo "}" >> /etc/logrotate.d/smi_slave

# Setting cron
COPY crons/cronjob /etc/cron.d/smi-cron
RUN chmod 0644 /etc/cron.d/smi-cron && \
    /usr/bin/crontab /etc/cron.d/smi-cron

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dataclasses

CMD cron && tail -f /smi-slave/logs/cronjobs_execution.log
