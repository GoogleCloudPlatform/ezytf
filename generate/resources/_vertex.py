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


from cdktf_cdktf_provider_google.vertex_ai_dataset import VertexAiDataset
from cdktf_cdktf_provider_google.vertex_ai_endpoint import VertexAiEndpoint
from cdktf_cdktf_provider_google.vertex_ai_deployment_resource_pool import (
    VertexAiDeploymentResourcePool,
    VertexAiDeploymentResourcePoolDedicatedResourcesAutoscalingMetricSpecsList,
)


def create_ai_dataset(self, ai_dataset):
    """creates ai_dataset"""
    name = ai_dataset["display_name"]
    ai_dataset["project"] = self.tf_ref("project", ai_dataset["project"])

    self.created["ai_dataset"][name] = VertexAiDataset(
        self, f"ai_dataset_{name}", **ai_dataset
    )


def generate_ai_dataset(self, my_resource, resource):
    """creates ai_dataset"""
    for data in self.eztf_config.get(my_resource, []):
        create_ai_dataset(self, data)


def create_ai_endpoint(self, ai_endpoint):
    """creates ai_endpoint"""
    name = ai_endpoint["display_name"]
    ai_endpoint["project"] = self.tf_ref("project", ai_endpoint["project"])

    if psc_proj := ai_endpoint.get("private_service_connect_config", {}).get(
        "project_allowlist"
    ):
        ai_endpoint["private_service_connect_config"]["project_allowlist"] = [
            self.tf_ref("project", project) for project in psc_proj
        ]

    self.created["ai_endpoint"][name] = VertexAiEndpoint(
        self, f"ai_endpoint_{name}", **ai_endpoint
    )


def generate_ai_endpoint(self, my_resource, resource):
    """creates ai_endpoint"""
    for data in self.eztf_config.get(my_resource, []):
        create_ai_endpoint(self, data)


def create_ai_resource_pool(self, ai_resource_pool):
    """creates ai_resource_pool"""
    name = ai_resource_pool["name"]
    ai_resource_pool["project"] = self.tf_ref("project", ai_resource_pool["project"])

    if dr := ai_resource_pool.get("dedicated_resources"):
        self.tf_param_list(
            dr.get("autoscaling_metric_specs"),
            "autoscaling_metric_specs",
            VertexAiDeploymentResourcePoolDedicatedResourcesAutoscalingMetricSpecsList,
        )

    self.created["ai_resource_pool"][name] = VertexAiDeploymentResourcePool(
        self, f"ai_resource_pool_{name}", **ai_resource_pool
    )


def generate_ai_resource_pool(self, my_resource, resource):
    """creates ai_resource_pool"""
    for data in self.eztf_config.get(my_resource, []):
        create_ai_resource_pool(self, data)
