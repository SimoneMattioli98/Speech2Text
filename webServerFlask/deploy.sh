#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Lo script richiede un parametro che corrisponde al nome del registry docker da utilizzare."
    exit 1
fi

IMAGE='s2t-labeler'
VERSION='1.0.2'

# Credo l'immagine in locale
docker build --network host -f ./Dockerfile -t ${1}/${IMAGE}:${VERSION} .

# Pusho l'immagine sul registry online
docker push ${1}/${IMAGE}:${VERSION}

echo ""
echo "Per la pubblicazione è necessario modificare la versione del container presente"
echo "nell'omonimo progetto in gitlab, in particolare nei file:"
echo "  - docker-compose.yml"
echo "  - webapp.yml"
echo ""
