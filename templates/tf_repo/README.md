### Prerequisite

Organization Admin IAM access 

__Load tf and other env variables__
```
source script_env
```

__Create bootstrap project, gcs & service account, enable apis__
```
./setup_project.sh
```

__For users or groups creation__

- [Create custom role with User & Group permission](https://support.google.com/a/answer/2406043?hl=en)   
- Assign Created service account (`TF_VAR_setup_service_account` in `script_env`) as admin to that role  



### Run Terraform
```
terraform init
terraform plan
terraform apply
```