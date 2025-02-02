### Prerequisite

Organization Admin IAM access 

__Load tf and other env variables__
```
source script_env
```

__Create bootstrap project, gcs & service account, enable apis__
```
bash setup_project.sh
```

__For users or groups creation__

- [Create custom role with user & group permission](https://support.google.com/a/answer/2406043?hl=en)   
- [Assign custom role to a service account](https://support.google.com/a/answer/9807615?hl=en#zippy=%2Cassign-a-role-to-a-service-account) (`setup_service_account` in `script_env`)



### Run Terraform
```
terraform init
terraform plan
terraform apply
```