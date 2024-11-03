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

FROM python:slim

ARG CDKTF_VERSION='0.20.9'
ARG TF_VERSION='1.9.8'
ARG NODE_VERSION="v20.17.0"

LABEL name="ezyTF"

RUN groupadd --gid 1000 ez && useradd --uid 1000 --gid ez --shell /bin/bash --create-home ez

RUN \
apt-get update && apt-get install curl gnupg2 xz-utils -yqq && \
apt-get upgrade -yqq && \
  rm -rf /var/lib/apt/lists/*

RUN ARCH= && dpkgArch="$(dpkg --print-architecture)" \
  && case "${dpkgArch##*-}" in \
    amd64) ARCH='x64';; \
    arm64) ARCH='arm64';; \
    *) echo "unsupported architecture"; exit 1 ;; \
  esac \
  && for key in $(curl -sL https://raw.githubusercontent.com/nodejs/docker-node/HEAD/keys/node.keys); do \
    gpg --batch --keyserver hkps://keys.openpgp.org --recv-keys "$key" || \
    gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "$key" ; \
  done \
  && curl -fsSLO --compressed "https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-$ARCH.tar.xz" \
  && curl -fsSLO --compressed "https://nodejs.org/dist/${NODE_VERSION}/SHASUMS256.txt.asc" \
  && gpg --batch --decrypt --output SHASUMS256.txt SHASUMS256.txt.asc \
  && grep " node-${NODE_VERSION}-linux-$ARCH.tar.xz\$" SHASUMS256.txt | sha256sum -c - \
  && tar -xJf "node-${NODE_VERSION}-linux-$ARCH.tar.xz" -C /usr/local --strip-components=1 --no-same-owner \
  && rm "node-${NODE_VERSION}-linux-$ARCH.tar.xz" SHASUMS256.txt.asc SHASUMS256.txt \
  && ln -s /usr/local/bin/node /usr/local/bin/nodejs
RUN corepack enable yarn

RUN pip install -U pip pipenv

RUN apt-get update && apt-get install -y --no-install-recommends git wget unzip

# USER ez
WORKDIR /app

RUN wget -O terraform.zip https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip && \
	unzip -o terraform.zip  && \
	rm terraform.zip  && \
	mv terraform /usr/local/bin/ 

# gcloud installation
RUN wget -O /tmp/google-cloud-sdk.tar.gz https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz && \
	mkdir -p /usr/local/gcloud && \
	tar -C /usr/local/gcloud -xf /tmp/google-cloud-sdk.tar.gz && \
	rm /tmp/google-cloud-sdk.tar.gz && \
	/usr/local/gcloud/google-cloud-sdk/install.sh --quiet
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

RUN mkdir -p /app/generate && mkdir -p /app/read_input

COPY ./generate/Pipfile ./generate/Pipfile.lock ./generate/cdktf.json ./generate/
RUN npm install --global cdktf-cli@latest && \
	cd generate && pipenv install --system && \
	cdktf get

COPY read_input/package.json ./read_input/
RUN cd read_input && npm install --omit=dev

COPY . .
RUN git config --global --add safe.directory '*'
RUN git config --global credential.'https://*.*.sourcemanager.dev'.helper gcloud.sh

# CMD ["/bin/bash", "generator.sh"]
CMD ["npm", "start", "--prefix", "read_input"]
