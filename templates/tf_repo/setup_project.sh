#!/bin/bash
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


gcloud projects create $setup_project_id

gcloud config set project $setup_project_id

gcloud iam service-accounts create $setup_service_account_name --display-name=$setup_service_account_name
# setup_service_account=$setup_service_account_name@$setup_project_id.iam.gserviceaccount.com

apis=(
	"serviceusage.googleapis.com"
	"cloudresourcemanager.googleapis.com"
	"cloudbilling.googleapis.com"
	"iam.googleapis.com"
	"admin.googleapis.com"
	"storage-api.googleapis.com"
	"logging.googleapis.com"
	"monitoring.googleapis.com"
	"orgpolicy.googleapis.com"
	"cloudidentity.googleapis.com"
)

roles=(
	"roles/resourcemanager.organizationAdmin"
	"roles/orgpolicy.policyAdmin"
	"roles/iam.organizationRoleAdmin"
	"roles/resourcemanager.folderAdmin"
	"roles/resourcemanager.folderIamAdmin"
	"roles/resourcemanager.projectCreator"
	"roles/securitycenter.admin"
	"roles/compute.networkAdmin"
	"roles/compute.xpnAdmin"
	"roles/compute.securityAdmin"
	"roles/iam.serviceAccountCreator"
	"roles/logging.admin"
	"roles/monitoring.admin"
	"roles/pubsub.admin"
	"roles/bigquery.admin"
	"roles/compute.instanceAdmin.v1"
	"roles/billing.user"
	"roles/serviceusage.serviceUsageConsumer"
)

# Enable APIs
for api in "${apis[@]}"; do
	echo "enabling api $api"
	gcloud services enable "$api"
done

# Create GCS State Bucket, add IAM to bucket
gcloud storage buckets create gs://$gcs_bucket --location=$gcs_bucket_location && \
gcloud storage buckets add-iam-policy-binding gs://$gcs_bucket \
	--member="serviceAccount:$setup_service_account" --role=roles/storage.legacyBucketWriter

# Add IAM role to service account at organization
for role in "${roles[@]}"; do
    gcloud organizations add-iam-policy-binding $organization_id \
        --role="$role" \
        --member="serviceAccount:$setup_service_account"
done

# Give service account, service account token creator role
gcloud iam service-accounts add-iam-policy-binding $setup_service_account \
	--member="serviceAccount:$setup_service_account" --role="roles/iam.serviceAccountTokenCreator"

# Give user service account user and token creator role
user_account=$(gcloud config list account --format "value(core.account)")
gcloud iam service-accounts add-iam-policy-binding $setup_service_account \
	--member="user:$user_account" --role="roles/iam.serviceAccountTokenCreator"

gcloud iam service-accounts add-iam-policy-binding $setup_service_account \
	--member="user:$user_account" --role="roles/iam.serviceAccountUser"
