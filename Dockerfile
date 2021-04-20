FROM python:3.6

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
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

# Setting cron
COPY crons/cronjob /etc/cron.d/smi-cron

RUN chmod 0644 /etc/cron.d/smi-cron

RUN /usr/bin/crontab /etc/cron.d/smi-cron

RUN pip install --no-cache-dir -r requirements.txt
