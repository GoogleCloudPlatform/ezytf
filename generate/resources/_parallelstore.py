# Copyright 2025 Google LLC
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
from cdktf_cdktf_provider_google.parallelstore_instance import ParallelstoreInstance

def create_parallelstore(self, parallelstore):
    """creates parallelstore"""
    name = parallelstore["instance_id"]
    parallelstore["project"] = self.tf_ref("project", parallelstore["project"])
    if parallelstore.get("network"):
        parallelstore["network"] = self.tf_ref("network", parallelstore["network"])
    

    self.created["parallelstore"][name] = ParallelstoreInstance(self, f"parallelstore_{name}", **parallelstore)


def generate_parallelstore(self, my_resource, resource):
    """creates parallelstore"""
    for data in self.eztf_config.get(my_resource, []):
        create_parallelstore(self, data)

