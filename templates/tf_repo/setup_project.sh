# required vars
# setup_project_id
# setup_apis # comma seperated apis to be enabled
# setup_roles # comma seperated roles to be given
# setup_service_account_name
# setup_gcs, setup_gcs_location # if gcs bucket is to be created 
# setup_iam_resource # either (projects, resource-manager folders, organizations)
# setup_iam_resource_id # either project_id, folder_id, organization_id

gcloud projects create $setup_project_id
gcloud config set project $setup_project_id

user_account=$(gcloud config list account --format 'value(core.account)')
user_principal="user:$user_account"
# user_principal="group:$group_account"

# {% if not setup_service_account_name %} 
runner_principal=$user_principal
# {% elif setup_service_account_name %} # --- Create & Use Service Account ---
gcloud iam service-accounts create $setup_service_account_name --display-name=$setup_service_account_name && \
setup_service_account=$setup_service_account_name@$setup_project_id.iam.gserviceaccount.com
runner_principal="serviceAccount:$setup_service_account"
gcloud iam service-accounts add-iam-policy-binding $setup_service_account --member=$runner_principal --role="roles/iam.serviceAccountTokenCreator"
gcloud iam service-accounts add-iam-policy-binding $setup_service_account --member=$user_principal --role="roles/iam.serviceAccountTokenCreator"
gcloud iam service-accounts add-iam-policy-binding $setup_service_account --member=$user_principal --role="roles/iam.serviceAccountUser"
# {% endif %}

IFS=','; setup_apis=($setup_apis); setup_roles=($setup_roles); unset IFS

# Enable APIs
for api in "${setup_apis[@]}"; do
	echo "enabling api $api"
	gcloud services enable "$api"
done

# Add IAM role to runner_principal account at organization
for role in "${setup_roles[@]}"; do
	gcloud $setup_iam_resource add-iam-policy-binding $setup_iam_resource_id --role="$role" --member=$runner_principal
done

# {% if setup_gcs %}
# Create GCS State Bucket, add IAM to bucket
gcloud storage buckets create gs://$setup_gcs --location=$setup_gcs_location
gcloud storage buckets add-iam-policy-binding gs://$setup_gcs --member=$runner_principal --role=roles/storage.legacyBucketWriter
# {% endif %}