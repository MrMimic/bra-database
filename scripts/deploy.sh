#!/usr/bin/env bash
set -ex

# Check utilities
gcloud --version
jq --version

# Authenticate docker on gcloud (gcloud auth login)

docker tag bra/backend gcr.io/data-baguette/bra-backend
docker push gcr.io/data-baguette/bra-backend
