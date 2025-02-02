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

from cdktf import TerraformHclModule
import util


def create_any_module(self, data, module_details, my_resource):
    module_id = data.get("_eztf_module_id", util.random_str(n=5))
    del data["_eztf_module_id"]
    args = {"variables": data, **module_details}
    name = f"{my_resource}_{module_id}"
    TerraformHclModule(self, name, **args)


def generate_any_module(self, my_resource, resource):
    """creates any module"""
    module_details = (
        self.eztf_config.get("eztf", {}).get("tf_any_module", {}).get(my_resource, {})
    )
    for data in self.eztf_config.get(my_resource, []):
        create_any_module(self, data, module_details, my_resource)
