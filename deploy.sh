#!/usr/bin/env bash
set -ex

ls -alstrh
echo $PWD

curl https://sdk.cloud.google.com > install.sh
bash install.sh --disable-prompts

gcloud --version
