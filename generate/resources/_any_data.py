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

# from cdktf_cdktf_provider_google.data_google_compute_network import DataGoogleComputeNetwork
import util


def data_function(name: str):
    provider = name.split("_")[0]
    method_name = util.pascal_case(f"data_{name}")
    module = __import__(f"cdktf_cdktf_provider_{provider}.data_{name}")
    func = getattr(module, method_name)
    return func


def create_any_data(self, data_name: str, data: dict):
    data_id = data.get("_eztf_data_id", util.random_str(n=5))
    del data["_eztf_data_id"]
    func = data_function(data_name)
    self.created["data"][data_name][data_id] = func(self, **data)


def generate_any_data(self, my_range, range):
    """creates any data"""
    data_details = (
        self.eztf_config.get("eztf", {}).get("tf_any_data", {}).get(my_range, {})
    )
    for data in self.eztf_config.get(my_range, []):
        create_any_data(self, data_details.get("name"), data)
