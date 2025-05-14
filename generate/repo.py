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
import util
import templating as templ

CONFIG_FILE = os.environ.get("EZTF_INPUT_CONFIG")
CONFIG_BUCKET = os.environ.get("EZTF_CONFIG_BUCKET")
OUTPUT_BUCKET = os.environ.get("EZTF_OUTPUT_BUCKET")
LOCAL_OUTPUT_DIR = os.environ.get("EZTF_OUTPUT_DIR") or "../ezytf-gen-data/eztf-output"
SSM_HOST = os.environ.get("EZTF_SSM_HOST")
EZTF_MODE = os.environ.get("EZTF_MODE")
EZTF_OUTPUT_GCS_PREFIX = os.environ.get("EZTF_OUTPUT_GCS_PREFIX")
CDKTF_OUTPUT_DIR = os.environ.get("EZTF_CDK_OUTPUT_DIR") or "cdktf.out"


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


def resource_in_stack(stack_dict, stack_name):
    tf_resources = []
    for rr in stack_dict.get(stack_name, []):
        for _, resource in rr.items():
            if resource not in tf_resources:
                tf_resources.append(resource)
    return tf_resources


def stack_variables(config, stack_name, merge_common_vars=False):
    if merge_common_vars:
        vars = copy.deepcopy(config.get("variable", {}))
    else:
        vars = {}
    for rr in config["eztf"]["stacks"].get(stack_name, []):
        for rng, res in rr.items():
            if res == "variable":
                vars.update(config.get(rng, {}))
    return vars


def tf_creator(repo_folder, config_dict, clean_org):
    "splits tf file"
    tfstacks = config_dict["eztf"].get("tf_stacks", [])
    tf_vars = config_dict["eztf"].get("tf_vars", {})
    stacks = config_dict["eztf"].get("stacks", {})
    vars = config_dict["variable"]

    for config_sub_stack in tfstacks:
        stack_name = f"gcp-{clean_org}-{config_sub_stack}"
        cdktf_out_file = util.cdktf_output(
            stack_name=stack_name, output_folder=CDKTF_OUTPUT_DIR
        )
        repo_subfolder_path = f"{repo_folder}/{config_sub_stack}"
        util.split_tf_file(cdktf_out_file, repo_subfolder_path)
        if stack_tf_vars := tf_vars.get(config_sub_stack):
            util.tf_vars_file(stack_tf_vars, repo_subfolder_path)
        tf_resources = resource_in_stack(stacks, config_sub_stack)
        stack_vars = stack_variables(config_dict, config_sub_stack)
        templ.create_templated_file(
            repo_subfolder_path, tf_resources + ["tf"], stack_vars
        )

    if len(tfstacks) > 0:
        templ.setup_script(repo_folder, vars, True)


def yaml_json_creator(repo_folder, config, range, resource, stack_name):
    "json yaml file creator"
    for i, item in enumerate(config.get(range, [])):
        my_item = copy.deepcopy(item)
        filename = ""
        if isinstance(my_item, dict) and my_item.get("eztf_filename"):
            filename = my_item.get("eztf_filename")
            del my_item["eztf_filename"]
        filename = util.eztf_filename(filename, resource, range, i)
        yield filename
        if resource == "yaml":
            util.write_file_yaml(f"{repo_folder}/{filename}", my_item)
        elif resource == "json":
            util.write_file_json(f"{repo_folder}/{filename}", my_item)


def anyfile_creator(repo_folder, config, range, resource, stack_name):
    "any file creator"
    for i, item in enumerate(config.get(range, [])):
        vars = copy.deepcopy(item)
        filename = item.get("eztf_filename", "")
        content = item.get("content", "")
        vars.pop("eztf_filename", None)
        vars.pop("content", None)
        filename = util.eztf_filename(filename, "", range, i)
        yield filename
        util.write_file_any(f"{repo_folder}/{filename}", content, vars, mode="a")


def jsonl_creator(repo_folder, config, range, resource, stack_name):
    "jsonl file creator"
    item = copy.deepcopy(config.get(range, []))
    filename = util.eztf_filename("", "jsonl", range, 0)
    util.write_file_jsonl(f"{repo_folder}/{filename}", item)
    yield filename


def curl_creator(repo_folder, config, range, resource, stack_name):
    "curl command creator"
    for i, item in enumerate(config.get(range, [])):
        my_item = copy.deepcopy(item)
        filename = ""
        content = []
        if isinstance(my_item, dict):
            filename = my_item.get("eztf_filename", "")
            my_item.pop("eztf_filename", None)
            content.append(util.generate_curl_command(**my_item))
        elif isinstance(my_item, list):
            for cmd in my_item:
                cmd.pop("eztf_filename", None)
                content.append(util.generate_curl_command(**cmd))
        filename = util.eztf_filename(filename, "sh", range, i)
        yield filename
        util.write_file_any(f"{repo_folder}/{filename}", "\n\n".join(content))


def cmd_creator(repo_folder, config, range, resource, stack_name):
    "cmd command creator"
    content = []
    for i, item in enumerate(config.get(range, [])):
        my_item = copy.deepcopy(item)
        cmd = my_item["cmd"]
        if isinstance(my_item, str):
            cmd = [cmd]
        content.append(
            util.generate_command(
                cmd, my_item.get("options", {}), my_item.get("vars", {})
            )
        )
    filename = util.eztf_filename("", "sh", range, 0)
    yield filename
    util.write_file_any(f"{repo_folder}/{filename}", "\n\n".join(content))


def setup_script_creator(repo_folder, config, range, resource, stack_name):
    "add scripts file and env var in repo folder"
    vars = stack_variables(config, stack_name)
    is_tf = True if stack_name in config.get("eztf", {}).get("tf_stacks", []) else False
    templ.setup_script(repo_folder, vars, is_tf)
    yield "script_env"


def env_var_creator(repo_folder, config, range, resource, stack_name):
    "add env var in repo folder if it contains non tf resource as well"
    stacks_resource = set(resource_in_stack(config["eztf"]["stacks"], stack_name))
    non_tf_stack = stacks_resource & {"file", "anyfile", "cmd", "curl"}
    if non_tf_stack:
        vars = config.get(range, {})
        non_tf_var = util.dict_without_prefixes(vars, ["setup_", "ez_"])
        if non_tf_var:
            content = util.python_to_bash_vars(non_tf_var, export=True)
            util.write_file_any(f"{repo_folder}/var_env", content)
            yield "var_env"


creator_function = {
    "yaml": yaml_json_creator,
    "json": yaml_json_creator,
    "jsonl": jsonl_creator,
    "anyfile": anyfile_creator,
    "file": anyfile_creator,
    "curl": curl_creator,
    "cmd": cmd_creator,
    "setup_script": setup_script_creator,
    "variable": env_var_creator,
}


def my_creator(repo_folder, config):
    "other supported file creator"
    for config_sub_stack, range_resource in config["eztf"]["stacks"].items():
        output_files = []
        repo_subfolder_path = f"{repo_folder}/{config_sub_stack}"
        for rr in range_resource:
            for range, resource in rr.items():
                if creator_function.get(resource):
                    filename_yield_op = creator_function[resource](
                        repo_subfolder_path, config, range, resource, config_sub_stack
                    )
                    if filename_yield_op:
                        output_files.extend(list(filename_yield_op))
        if output_files:
            print(
                f"Created files: {','.join(output_files)} in {'/'.join(repo_subfolder_path.split('/')[-2:])}"
            )
    templ.create_templated_file(
        repo_folder, ["_root"], {"stack_list": config["eztf"]["stacks"].keys()}
    )


def main(config_dict):
    variable = config_dict["variable"]
    domain = variable["domain"]
    config_type = variable.get("ez_config_name") or "ezy"
    config_git_uri = variable.get("ez_repo_git_uri", "")

    clean_domain = util.clean_res_id(domain)
    repo = f"gcp-{clean_domain}-{config_type}"
    output_folder = f"{LOCAL_OUTPUT_DIR}/{repo}"

    util.delete_folders([output_folder])
    my_creator(output_folder, config_dict)
    tf_creator(output_folder, config_dict, clean_domain)
    code_push_remote(repo, output_folder, config_git_uri)

    return output_folder


if __name__ == "__main__":
    config_dict = util.get_file_yaml(CONFIG_FILE)
    output_folder = main(config_dict)
    if EZTF_MODE == "service":
        util.delete_folders([output_folder, CDKTF_OUTPUT_DIR])
