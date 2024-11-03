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

from cdktf import (
    TerraformIterator,
    Token,
)
from cdktf_cdktf_provider_google.project_service import ProjectService
from imports.project_services import ProjectServices


def enable_api(self, projects, api):
    api_projects = [self.tf_ref("project", project) for project in projects]
    iterator = TerraformIterator.from_list(api_projects)
    ProjectService(
        self,
        f"api_n_prj_{api}",
        for_each=iterator,
        service=api,
        disable_on_destroy=False,
        disable_dependent_services=False,
        project=Token.as_string(iterator.value),
    )


def create_project_services(self, api_svc):
    """creates project_services"""
    name = api_svc["project_id"]
    api_svc["project_id"] = self.tf_ref("project", api_svc["project_id"])

    ProjectServices(self, f"api_prj_{name}", **api_svc)


def generate_project_services(self, my_resource, resource):
    """creates project_services"""
    for data in self.eztf_config.get(my_resource, []):
        create_project_services(self, data)
