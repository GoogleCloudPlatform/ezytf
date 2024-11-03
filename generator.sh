#!/bin/sh
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -eo pipefail

echo $EZTF_ACCESS_TOKEN_FILE
# Setting gcloud config
if [ -f "${EZTF_ACCESS_TOKEN_FILE}" ]; then
    gcloud config set auth/access_token_file $EZTF_ACCESS_TOKEN_FILE
fi

if [[ "${EZTF_MODE}" != "workflow" ]]; then
    npm run --prefix read_input read-generate
fi

if [[ "${EZTF_MODE}" == "workflow" ]]; then
    cd generate && cdktf synth --hcl &&
        python repo.py
fi
