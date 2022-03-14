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

jq -n "{type:\"$GCLOUD_TYPE\",project_id:\"$GCLOUD_PROJECT_ID\",private_key_id:\"$GCLOUD_PRIVATE_KEY_ID\",private_key:\"coucou\",client_email:\"$GCLOUD_CLIENT_EMAIL\",client_id:\"$GCLOUD_CLIENT_ID\",auth_uri:\"$GCLOUD_AUTH_URI\",token_uri:\"$GCLOUD_TOKEN_URI\",auth_provider_x509_cert_url:\"$GCLOUD_AUTH_PROVIDER_X509\",client_x509_cert_url:\"$GCLOUD_CLIENT_X509\"}" > gcloud_auth.json

echo "===="
cat gcloud_auth.json
echo "===="

gcloud auth login --no-browser --brief --cred-file=gcloud_auth.json

docker tag bra/backend gcr.io/data-baguette/bra-backend
docker push gcr.io/data-baguette/bra-backend
