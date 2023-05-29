# ================================================================
# Dockerfile para DEV com mais ferramentas
# ================================================================
FROM python:3.11.2-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    logrotate \
    cron \
    tzdata \
    postgresql-client \
    locales \
    iputils-ping \
    net-tools \
    dnsutils \
    curl \
    git \
    zsh \
    powerline \
    curl \
    wget &&\
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


# --------------------------------< config terminal >--------------------------------------

RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.2/zsh-in-docker.sh)" -- \
    -t https://github.com/romkatv/powerlevel10k \
    -p git \
    -p git-flow \
    -p https://github.com/zdharma-continuum/fast-syntax-highlighting \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions \
    -a 'export TERM=xterm-256color'


RUN echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ~/.zshrc && \
    echo 'HISTFILE=/home/python/zsh/.zsh_history' >> ~/.zshrc 


# ----------------------------------< cron >-----------------------------------------------
COPY crons/cronjob /etc/cron.d/sige-cron
RUN chmod 0644 /etc/cron.d/sige-cron && \
    /usr/bin/crontab /etc/cron.d/sige-cron

CMD ["/sige-slave/scripts/start.sh"]
