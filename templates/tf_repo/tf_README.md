## Run Terraform
State will be stored in gcs bucket mentioned `backend.tf` \
Export env variable (if not already done through `script_env` file)

```
# update SA_NAME & PROJECT_ID
export GOOGLE_IMPERSONATE_SERVICE_ACCOUNT=SA_NAME@PROJECT_ID.iam.gserviceaccount.com # when SA is used to run tf
export USER_PROJECT_OVERRIDE=true
export GOOGLE_BILLING_PROJECT=PROJECT_ID
export GOOGLE_PROJECT=PROJECT_ID # default google provider project
```

```
terraform init
terraform plan
terraform apply
```