#!/bin/sh
set -eo pipefail

echo $EZTF_ACCESS_TOKEN_FILE
# Setting gcloud config
if [ -f "${EZTF_ACCESS_TOKEN_FILE}" ]; then
    gcloud config set auth/access_token_file $EZTF_ACCESS_TOKEN_FILE
fi

if [[ "${EZTF_MODE}" != "workflow" ]]; then
    npm run --prefix read_input read
fi

if [[ "${EZTF_MODE}" == "workflow" ]]; then
    cd generate && cdktf synth --hcl &&
        python repo.py
fi
