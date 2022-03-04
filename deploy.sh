#!/usr/bin/env bash
set -ex

ls -alstrh
echo $PWD
echo $HOME

if [ -f /home/travis/google-cloud-sdk ]; then
    rm /home/travis/google-cloud-sdk
fi

curl https://sdk.cloud.google.com > install.sh
bash install.sh --disable-prompts

gcloud --version
