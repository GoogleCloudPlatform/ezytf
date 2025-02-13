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

import os
import copy
import shutil
import util

CONFIG_FILE = os.environ.get("EZTF_INPUT_CONFIG")
CONFIG_BUCKET = os.environ.get("EZTF_CONFIG_BUCKET")
OUTPUT_BUCKET = os.environ.get("EZTF_OUTPUT_BUCKET")
LOCAL_OUTPUT_DIR = os.environ.get("EZTF_OUTPUT_DIR") or "../ezytf-gen-data/eztf-output"
SSM_HOST = os.environ.get("EZTF_SSM_HOST")
EZTF_MODE = os.environ.get("EZTF_MODE")
EZTF_OUTPUT_GCS_PREFIX = os.environ.get("EZTF_OUTPUT_GCS_PREFIX")
CDKTF_OUTPUT_DIR = os.environ.get("EZTF_CDK_OUTPUT_DIR") or "cdktf.out"
REPO_TEMPLATE_FILE = [
    "../templates/tf_repo/setup_project.sh",
    "../templates/tf_repo/README.md",
]
EX_VAR_ENV = {
    "setup_project_id",
    "setup_service_account_name",
    "gcs_bucket",
    "gcs_bucket_location",
    "organization_id",
    "setup_service_account",
}


def code_push_remote(repo_name, repo_folder, git_uri):
    """pushed to remote repository/bucket"""
    if OUTPUT_BUCKET:
        gcs_prefix = (
            EZTF_OUTPUT_GCS_PREFIX
            or f"eztf-output/{repo_name}/{repo_name}-{util.time_str()}/"
        )
        util.upload_folder_to_gcs_parallel(OUTPUT_BUCKET, repo_folder, gcs_prefix)

    if SSM_HOST and not git_uri:
        git_uri = util.ssm_repository(repo_name, SSM_HOST)

    if git_uri:
        util.push_folder_to_git(repo_folder, git_uri, "auto")


def tf_creator(repo_folder, clean_org, tfstacks, stacks_variable):
    "splits tf file"
    for config_sub_stack in tfstacks:
        stack_name = f"gcp-{clean_org}-{config_sub_stack}"
        cdktf_out_file = util.cdktf_output(
            stack_name=stack_name, output_folder=CDKTF_OUTPUT_DIR
        )
        repo_subfolder_path = f"{repo_folder}/{config_sub_stack}"
        util.split_tf_file(cdktf_out_file, repo_subfolder_path)
        if stacks_variable.get(config_sub_stack):
            util.tf_vars_file(stacks_variable[config_sub_stack], repo_subfolder_path)


def yaml_json_creator(repo_folder, resource, data):
    "json yaml file creator"
    for my_item in data:
        item = copy.deepcopy(my_item)
        filename = my_item.get("eztf_filename", util.random_str(n=5))
        del item["eztf_filename"]
        if not filename.endswith(f".{resource}"):
            filename += f".{resource}"
        if resource == "yaml":
            util.write_file_yaml(f"{repo_folder}/{filename}", item)
        elif resource == "json":
            util.write_file_json(f"{repo_folder}/{filename}", item)


def anyfile_creator(repo_folder, resource, data):
    "any file creator"
    for item in data:
        filename = item.get("eztf_filename", util.random_str(n=5))
        util.write_file_any(f"{repo_folder}/{filename}", item.get("content", ""))


creator_function = {
    "yaml": yaml_json_creator,
    "json": yaml_json_creator,
    "anyfile": anyfile_creator,
}


def my_creator(repo_folder, config):
    "other supported file creator"
    for config_sub_stack, range_resource in config["eztf"]["stacks"].items():
        repo_subfolder_path = f"{repo_folder}/{config_sub_stack}"
        for rr in range_resource:
            for range, resource in rr.items():
                if creator_function.get(resource):
                    creator_function[resource](
                        repo_subfolder_path, resource, config.get(range)
                    )


def add_setup_scripts(repo_folder, tf_vars):
    "add scripts file and env var in repo folder"
    script_var = {}

    for var in EX_VAR_ENV.intersection(tf_vars):
        script_var[var] = tf_vars[var]

    if not script_var.get("setup_service_account"):
        sa_name = script_var.get("setup_service_account_name", "")
        sa_proj = script_var.get("setup_project_id", "")
        script_var["setup_service_account"] = (
            f"{sa_name}@{sa_proj}.iam.gserviceaccount.com"
        )

    if script_var.get("setup_service_account"):
        script_var["GOOGLE_IMPERSONATE_SERVICE_ACCOUNT"] = script_var[
            "setup_service_account"
        ]
    if script_var.get("setup_project_id"):
        script_var["USER_PROJECT_OVERRIDE"] = "true"
        script_var["GOOGLE_BILLING_PROJECT"] = script_var["setup_project_id"]

    env_str = "\n".join(
        [f"export {name}={value}" for name, value in script_var.items()]
    )

    with open(f"{repo_folder}/script_env", "w", encoding="utf-8") as script_env:
        script_env.write(env_str)

    for template_file in REPO_TEMPLATE_FILE:
        dest_file = os.path.join(repo_folder, os.path.basename(template_file))
        shutil.copy2(template_file, dest_file)


if __name__ == "__main__":
    config_dict = util.get_file_yaml(CONFIG_FILE)
    variable = config_dict["variable"]
    domain = variable["domain"]
    config_type = variable.get("eztf_config_name") or "ezytf"
    tfstacks = config_dict["eztf"].get("tf_stacks", [])
    stack_variables = config_dict["eztf"].get("tf_vars", {})
    config_git_uri = variable.get("output_git_uri", "")
    clean_domain = util.clean_res_id(domain)
    repo = f"gcp-{clean_domain}-{config_type}"
    output_folder = f"{LOCAL_OUTPUT_DIR}/{repo}"
    tf_creator(output_folder, clean_domain, tfstacks, stack_variables)
    my_creator(output_folder, config_dict)
    add_setup_scripts(output_folder, variable)
    code_push_remote(repo, output_folder, config_git_uri)
    if EZTF_MODE == "service":
        # print(f"cleaning up {output_folder} and {CDKTF_OUTPUT_DIR}")
        shutil.rmtree(output_folder)
        shutil.rmtree(CDKTF_OUTPUT_DIR)
