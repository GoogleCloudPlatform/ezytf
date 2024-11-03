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

FROM nikolaik/python-nodejs:python3.12-nodejs20-alpine

ARG CDKTF_VERSION='0.20.9'
ARG TF_VERSION='1.9.8'

LABEL name="ezyTF"

# USER pn
WORKDIR /app

RUN apk add git && \
	wget -O terraform.zip https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip && \
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

# CMD ["sh", "generator.sh"]
CMD ["npm", "start", "--prefix", "read_input"]
