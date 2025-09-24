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


from cdktf_cdktf_provider_google.vertex_ai_index import VertexAiIndex
from cdktf_cdktf_provider_google.vertex_ai_index_endpoint import VertexAiIndexEndpoint
from cdktf_cdktf_provider_google.vertex_ai_index_endpoint_deployed_index import (
    VertexAiIndexEndpointDeployedIndex,
)


def create_ai_index(self, ai_index):
    """creates ai_index"""
    name = ai_index["display_name"]
    ai_index["project"] = self.tf_ref("project", ai_index["project"])

    self.created["ai_index"][name] = VertexAiIndex(self, f"ai_index_{name}", **ai_index)


def generate_ai_index(self, my_resource, resource):
    """creates ai_index"""
    for data in self.eztf_config.get(my_resource, []):
        create_ai_index(self, data)


def create_ai_index_endpoint(self, ai_index_endpoint):
    """creates ai_index_endpoint"""
    name = ai_index_endpoint["display_name"]
    ai_index_endpoint["project"] = self.tf_ref("project", ai_index_endpoint["project"])

    if psc_proj := ai_index_endpoint.get("private_service_connect_config", {}).get(
        "project_allowlist"
    ):
        ai_index_endpoint["private_service_connect_config"]["project_allowlist"] = [
            self.tf_ref("project", project) for project in psc_proj
        ]

    self.created["ai_index_endpoint"][name] = VertexAiIndexEndpoint(
        self, f"ai_index_endpoint_{name}", **ai_index_endpoint
    )


def generate_ai_index_endpoint(self, my_resource, resource):
    """creates ai_index_endpoint"""
    for data in self.eztf_config.get(my_resource, []):
        create_ai_index_endpoint(self, data)


def create_deployed_index(self, deployed_index):
    """creates deployed_index"""
    name = deployed_index["deployed_index_id"]
    deployed_index["project"] = self.tf_ref("project", deployed_index["project"])
    deployed_index["index"] = self.tf_ref("ai_index", deployed_index["index"])
    deployed_index["index_endpoint"] = self.tf_ref(
        "ai_index_endpoint", deployed_index["index_endpoint"]
    )

    self.created["ai_deployed_index"][name] = VertexAiIndexEndpointDeployedIndex(
        self, f"deployed_index_{name}", **deployed_index
    )


def generate_deployed_index(self, my_resource, resource):
    """creates deployed_index"""
    for data in self.eztf_config.get(my_resource, []):
        create_deployed_index(self, data)
