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

from imports.project_factory import ProjectFactory
from imports.ff_project import FfProject
from imports.fabric_net_svpc_access import FabricNetSvpcAccess


def create_project(self, project):
    project_id = project["name"]
    project["org_id"] = self.tf_ref("organization", "/")
    project["billing_account"] = self.tf_ref("billing", project.get("billing_account"))
    project["name"] = project_id + self.created["vars"]["project_suffix"].string_value

    if folder := project.get("folder_id"):
        if self.which_node(folder) == "folder":
            project["folder_id"] = self.tf_ref("folder", folder)
    if svpc_host := project.get("svpc_host_project_id"):
        project["svpc_host_project_id"] = self.tf_ref("project", svpc_host)
    if group_name := project.get("group_name"):
        group_id = f'{group_name}@{project.get("domain","")}'
        project["group_name"] = self.tf_ref("group_name", group_id, group_name)

    added_project = ProjectFactory(self, f"prj_{project_id}", **project)

    if shared_subnets := project.get("shared_vpc_subnets"):
        added_project.add_override(
            "shared_vpc_subnets",
            [self.tf_ref("subnet", region_subnet) for region_subnet in shared_subnets],
        )
    self.created["projects"][project_id] = added_project


def create_ff_project(self, project):
    project_id = project.get("prefix", "") + project["name"]
    project["billing_account"] = self.tf_ref("billing", project.get("billing_account"))

    if project.get("parent"):
        node = self.which_node(project["parent"])
        project["parent"] = self.tf_ref(node, project["parent"])

    if project.get("shared_vpc_host_config", {}).get("enabled") is True:
        project["service_projects"] = [
            self.tf_ref("project", svc_project)
            for svc_project in project.get("shared_vpc_host_config", {}).get(
                "service_projects", []
            )
        ]

    self.update_fabric_iam(project)
    for tag_type in ["tags", "network_tags"]:
        for _, values in project.get(tag_type, {}).items():
            self.update_fabric_iam(values)
            for _, tagvalues in values.get("values", {}).items():
                self.update_fabric_iam(tagvalues)

    added_project = FfProject(self, f"prj_{project_id}", **project)

    if shared_subnets := project.get("shared_vpc_subnets"):
        added_project.add_override(
            "shared_vpc_subnets",
            [self.tf_ref("subnet", region_subnet) for region_subnet in shared_subnets],
        )
    self.created["projects"][project_id] = added_project


def generate_projects(self, my_resource, resource):
    for project in self.eztf_config.get(my_resource, []):
        if project.get("svpc_host_project_id"):
            continue
        create_project(self, project)
    generate_svc_projects(self, my_resource)


def generate_svc_projects(self, my_resource):
    add_svc_projects = [
        project
        for project in self.eztf_config.get(my_resource, [])
        if project.get("svpc_host_project_id")
    ]
    if add_svc_projects:
        self.file_seprator_variable("svcprojects", force=True)
    for project in add_svc_projects:
        create_project(self, project)


def generate_ff_projects(self, my_resource, resource):
    for project in self.eztf_config.get(my_resource, []):
        create_ff_project(self, project)


# Fabric


def create_svpc_access(self, svc):
    project_id = svc["host_project_id"]

    if svc_proj := svc.get("service_project_ids"):
        svc["service_project_ids"] = [
            self.tf_ref("project", project) for project in svc_proj
        ]

    FabricNetSvpcAccess(self, f"svpc_{project_id}", **svc)


def generate_svpc_access(self, my_resource, resource):
    for project in self.eztf_config.get(my_resource, []):
        create_svpc_access(self, project)
