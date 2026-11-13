# ==============================================================================
# ezytf Makefile
# ==============================================================================
# Load environment variables from .env if present
-include .env
export

# Default values if not set in .env or environment
GCP_REGION        ?= us-central1
IMAGE_REPO        ?= us-docker.pkg.dev/$(GCP_PROJECT_ID)/ezy/ezytf
IMAGE_TAG         ?= latest
CLOUD_RUN_SERVICE ?= ezytf
CLOUD_RUN_JOB     ?= gcp-cdk-tf
PORT              ?= 8080
HOST_PORT         ?= 8080
ADC_PATH          ?= $(HOME)/.config/gcloud/application_default_credentials.json

.PHONY: help build push deploy-cloud-run deploy-cloud-run-job run-docker run-docker-interactive run-local run-local-script clean

# ------------------------------------------------------------------------------
# Help (Default Target)
# ------------------------------------------------------------------------------
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ------------------------------------------------------------------------------
# Container Build & Push
# ------------------------------------------------------------------------------
build: ## Build the Docker image locally
	docker build -t $(IMAGE_REPO):$(IMAGE_TAG) . -f Dockerfile

push: ## Push the Docker image to Artifact Registry / Container Registry
	docker push $(IMAGE_REPO):$(IMAGE_TAG)

# ------------------------------------------------------------------------------
# Cloud Run Deployment
# ------------------------------------------------------------------------------
deploy-cloud-run: ## Deploy the container image to Cloud Run (Service)
	@echo "Deploying $(IMAGE_REPO):$(IMAGE_TAG) to Cloud Run service '$(CLOUD_RUN_SERVICE)'..."
	gcloud run deploy $(CLOUD_RUN_SERVICE) \
		--image=$(IMAGE_REPO):$(IMAGE_TAG) \
		--project=$(GCP_PROJECT_ID) \
		--region=$(GCP_REGION) \
		--memory 4Gi \
		--cpu 2000m \
		--min-instances 1 \
		--max-instances 2 \
		--execution-environment gen2 \
		--no-cpu-throttling \
		$(if $(CLOUD_RUN_SA),--service-account $(CLOUD_RUN_SA)) \
		--set-env-vars CI=1,EZTF_MODE=$(EZTF_MODE),EZTF_SSM_HOST=$(EZTF_SSM_HOST) \
		$(if $(EZTF_SSM_PROJECT),--set-env-vars EZTF_SSM_PROJECT=$(EZTF_SSM_PROJECT))

deploy-cloud-run-job: ## Update Cloud Run Job with the new container image
	@echo "Updating Cloud Run job '$(CLOUD_RUN_JOB)' with $(IMAGE_REPO):$(IMAGE_TAG)..."
	gcloud run jobs update $(CLOUD_RUN_JOB) \
		--image=$(IMAGE_REPO):$(IMAGE_TAG) \
		--project=$(GCP_PROJECT_ID) \
		--region=$(GCP_REGION) \
		--set-env-vars CI=1,EZTF_MODE=generate_job,EZTF_SSM_HOST=$(EZTF_SSM_HOST)

# ------------------------------------------------------------------------------
# Docker Local Execution
# ------------------------------------------------------------------------------
run-docker: ## Run the container locally in service mode (HTTP)
	@echo "Starting ezytf in Docker on http://localhost:$(HOST_PORT)..."
	docker run -p $(HOST_PORT):$(PORT) \
		-e PORT=$(PORT) \
		-e EZTF_MODE=$(EZTF_MODE) \
		-e EZTF_SSM_HOST=$(EZTF_SSM_HOST) \
		-e GOOGLE_CLOUD_PROJECT=$(GCP_PROJECT_ID) \
		-e GOOGLE_APPLICATION_CREDENTIALS=/tmp/google_adc.json \
		$(if $(EZTF_SHEET_ID),-e EZTF_SHEET_ID=$(EZTF_SHEET_ID)) \
		$(if $(EZTF_CONFIG_BUCKET),-e EZTF_CONFIG_BUCKET=$(EZTF_CONFIG_BUCKET)) \
		$(if $(EZTF_OUTPUT_BUCKET),-e EZTF_OUTPUT_BUCKET=$(EZTF_OUTPUT_BUCKET)) \
		$(if $(EZTF_SSH_PVT_KEY),-e EZTF_SSH_PVT_KEY="$(EZTF_SSH_PVT_KEY)") \
		-v $(ADC_PATH):/tmp/google_adc.json:ro \
		-v $(shell pwd)/ezytf-gen-data:/app/ezytf-gen-data \
		$(IMAGE_REPO):$(IMAGE_TAG)

run-docker-interactive: ## Run the container interactively with a bash shell
	@echo "Starting ezytf in Docker (interactive)..."
	docker run -it \
		-e EZTF_MODE=$(EZTF_MODE) \
		-e EZTF_SSM_HOST=$(EZTF_SSM_HOST) \
		-e GOOGLE_CLOUD_PROJECT=$(GCP_PROJECT_ID) \
		-e GOOGLE_APPLICATION_CREDENTIALS=/tmp/google_adc.json \
		$(if $(EZTF_SHEET_ID),-e EZTF_SHEET_ID=$(EZTF_SHEET_ID)) \
		-v $(ADC_PATH):/tmp/google_adc.json:ro \
		-v $(shell pwd)/ezytf-gen-data:/app/ezytf-gen-data \
		$(IMAGE_REPO):$(IMAGE_TAG) /bin/bash

# ------------------------------------------------------------------------------
# Local Execution (Without Docker)
# ------------------------------------------------------------------------------
run-local: ## Run the application locally in service mode (without Docker)
	@echo "Starting ezytf locally (service mode)..."
	cd read_input && npm start

run-local-script: ## Run the application locally in script mode (without Docker)
	@echo "Starting ezytf locally (script mode)..."
	cd read_input && npm run read-generate

# ------------------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------------------
clean: ## Remove locally built Docker image
	-docker rmi $(IMAGE_REPO):$(IMAGE_TAG)
