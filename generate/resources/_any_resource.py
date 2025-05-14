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

# from cdktf_cdktf_provider_google.compute_network import ComputeNetwork
import util


def create_any_resource(self, resource_name: str, res: dict):
    resource_id = res.get("_eztf_resource_id", util.random_str(n=5))
    del res["_eztf_resource_id"]
    func, res_name = self.resource_function(resource_name)
    if res.get("project"):
        res["project"] = self.tf_ref("project", res["project"])
    formatted_res = util.nested_list_keys_to_camel(res)
    self.created["resource"][resource_name][resource_id] = func(
        self, id_=f"{res_name}_{resource_id}", **formatted_res
    )


def generate_any_resource(self, my_resource, resource):
    """creates any resource"""
    resource_details = (
        self.eztf_config.get("eztf", {}).get("tf_any_resource", {}).get(my_resource, {})
    )
    resource_name = resource_details.get("name")
    if not resource_name:
        return
    self.created["resource"][resource_name] = self.created["resource"].get(
        resource_name, {}
    )
    for res in self.eztf_config.get(my_resource, []):
        create_any_resource(self, resource_name, res)
