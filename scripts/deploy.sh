#!/usr/bin/env bash
set -ex

# Remove the existing gcloud SDK and install last verison
if [ -f /home/travis/google-cloud-sdk ]; then
    rm /home/travis/google-cloud-sdk
fi
curl https://sdk.cloud.google.com > install.sh
bash install.sh --disable-prompts

# Check utilities
gcloud --version
jq --version

# Authenticate gcloud
echo ${GCLOUD_AUTH} | base64 --decode -i > gcloud-service-key.json
gcloud auth activate-service-account --key-file gcloud-service-key.json

docker tag bra/backend gcr.io/data-baguette/bra-backend
docker push gcr.io/data-baguette/bra-backend
