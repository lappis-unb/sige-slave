FROM python:3.11.2-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    postgresql-client \
    locales \
    iputils-ping \
    net-tools \
    dnsutils \
    curl \
    wget\
    locales &&\
    apt-get autoremove -y &&\
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

ARG API_KEY

RUN wget https://cronitor.io/dl/linux_amd64.tar.gz \
    && tar xvf linux\_amd64.tar.gz -C /usr/local/bin/ \
    && cronitor configure --api-key ${API_KEY}

WORKDIR /sige-slave
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ----------------------------< locale and timezone >-------------------------------------
RUN sed -i 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen pt_BR.UTF-8 \
    && dpkg-reconfigure --frontend noninteractive locales \
    && ln -snf /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \ 
    && echo "America/Sao_Paulo" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

# ----------------------------------< cron >-----------------------------------------------
COPY crons/cronjob /etc/cron.d/sige-cron
RUN chmod 0644 /etc/cron.d/sige-cron && \
    /usr/bin/crontab /etc/cron.d/sige-cron

CMD ["/sige-slave/scripts/start.sh"]
