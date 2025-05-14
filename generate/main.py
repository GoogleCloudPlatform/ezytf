#!/usr/bin/env python
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
import yaml
from cdktf import App
import util
from resources import MyStack, creation

app = App()


def run_cdktf(config):
    """run cdktf stack"""
    config["eztf"]["tf_vars"] = config["eztf"].get("tf_vars", {})
    domain = config["variable"]["domain"]
    config_stack = config["eztf"]["stacks"]
    tfstacks = set(config["eztf"].get("tf_stacks", []))

    for sub_stack, range_resources in config_stack.items():
        if sub_stack not in tfstacks:
            continue
        config["eztf"]["tf_vars"][sub_stack] = config["eztf"]["tf_vars"].get(
            sub_stack, {}
        )
        stack_name = f"gcp-{util.clean_res_id(domain)}-{sub_stack}"
        eztf_config = copy.deepcopy(config)
        app_stack = MyStack(app, stack_name, eztf_config, sub_stack, range_resources)
        config["eztf"]["tf_vars"][sub_stack] = app_stack.tf_vars

    return config


def is_stack_tf(eztf_range_resources):
    for range_resource in eztf_range_resources:
        for _, resource in range_resource.items():
            if creation.get(resource):
                return True
    return False


def tf_stacks(config_stack):
    tfstacks = []
    for sub_stack, range_resources in config_stack.items():
        if is_stack_tf(range_resources):
            tfstacks.append(sub_stack)
    return tfstacks


if __name__ == "__main__":
    CONFIG_BUCKET = os.environ.get("EZTF_CONFIG_BUCKET")
    CONFIG_FILE = os.environ.get("EZTF_INPUT_CONFIG")
    if not CONFIG_FILE:
        raise ValueError("EZTF_INPUT_CONFIG missing")

    if CONFIG_BUCKET:
        config_yaml = util.download_from_gcs(CONFIG_BUCKET, CONFIG_FILE)
        config_dict = yaml.safe_load(config_yaml)
    else:
        config_dict = util.get_file_yaml(CONFIG_FILE)

    tfstack = tf_stacks(config_dict["eztf"]["stacks"])
    config_dict["eztf"]["tf_stacks"] = tfstack
    if tfstack:
        config_dict = run_cdktf(config_dict)
    app.synth()
    util.write_file_yaml(CONFIG_FILE, config_dict)
