#!/bin/bash

IMAGE_NAME="sige"
IMAGE_TAG="latest"

# Verifica se a imagem existe localmente
if docker image inspect ${IMAGE_NAME}:${IMAGE_TAG} >/dev/null 2>&1; then
    echo "A imagem ${IMAGE_NAME}:${IMAGE_TAG} já existe. Pulando a etapa de pull."
else
    echo "A imagem ${IMAGE_NAME}:${IMAGE_TAG} não existe. Realizando o build."
    docker-compose build
fi

# Executa o comando pull ou up
docker-compose pull
# ou
# docker-compose up
