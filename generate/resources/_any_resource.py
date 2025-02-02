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

# from cdktf_cdktf_provider_google.google_compute_network import GoogleComputeNetwork
import util


def resource_function(name: str):
    provider = name.split("_")[0]
    method_name = util.pascal_case(name)
    module = __import__(f"cdktf_cdktf_provider_{provider}.{name}")
    func = getattr(module, method_name)
    return func


def create_any_resource(self, resource_name: str, res: dict):
    resource_id = res.get("_eztf_resource_id", util.random_str(n=5))
    del res["_eztf_resource_id"]
    func = resource_function(resource_name)
    self.created["resource"][resource_name][resource_id] = func(self, **res)


def generate_any_resource(self, my_resource, resource):
    """creates any resource"""
    resource_details = (
        self.eztf_config.get("eztf", {}).get("tf_any_resource", {}).get(my_resource, {})
    )
    for res in self.eztf_config.get(my_resource, []):
        create_any_resource(self, resource_details.get("name"), res)
