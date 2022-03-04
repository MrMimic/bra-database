#!/usr/bin/env bash
set -ex

if [ -f ${HOME}/google-cloud-sdk ]; then
    rm ${HOME}/google-cloud-sdk
fi
curl https://sdk.cloud.google.com | bash -s -- --disable-prompts > /dev/null
export PATH=${HOME}/google-cloud-sdk/bin:${PATH}
gcloud --version
