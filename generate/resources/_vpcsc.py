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

from imports.google.access_context_manager_access_policy import (
    AccessContextManagerAccessPolicy,
)
from imports.sc_access_level import ScAccessLevel
from imports.sc_perimeter import ScPerimeter
from imports.sc_perimeter_bridge import ScPerimeterBridge
from imports.null.resource import Resource
from imports.null.provider import NullProvider
from cdktf import LocalExecProvisioner


def create_null_resource(self, depends_on):
    """creates null resource"""
    NullProvider(self, "null")
    self.created["null"]["wait_for_members"] = Resource(
        self,
        "wait_for_members",
        provisioners=[LocalExecProvisioner(type="local-exec", command="sleep 60")],
    )
    self.created["null"]["wait_for_members"].add_override(
        "depends_on", [name for name in depends_on]
    )


def create_sc_policy(self, data):
    """creates sc policy"""
    name = data["title"]
    data["parent"] = f'organizations/{self.tf_ref("organization", "")}'
    scopes = data.get("scopes", [])
    new_scopes = []
    for scope in scopes:
        tf_scope = self.tf_ref("projects/number", scope)
        if tf_scope == scope:
            tf_scope = self.tf_ref("folder", scope)
        new_scopes.append(tf_scope)
    if new_scopes:
        data["scopes"] = new_scopes
    self.created["sc_policy"][name] = AccessContextManagerAccessPolicy(
        self, f"sc_policy_{name}", **data
    )


def create_sc_access_level(self, data):
    """creates sc access level"""
    name = data["name"]
    data["policy"] = self.tf_ref("sc_policy", data["policy"])
    self.created["sc_access_level"][name] = ScAccessLevel(
        self, f"sc_access_level_{name}", **data
    )


def create_sc_perimeter(self, data):
    """creates sc perimeter"""
    name = data["perimeter_name"]
    data["policy"] = self.tf_ref("sc_policy", data["policy"])
    data["description"] = (
        f'regular perimeter {name} {self.created["null"]["wait_for_members"].id}'
    )
    perimeter_al = []
    for al in data.get("access_levels", []):
        tf_al = self.tf_ref("sc_access_level_name", al)
        perimeter_al.append(tf_al)
    if perimeter_al:
        data["access_levels"] = perimeter_al
    for policy in data.get("ingress_policies", []):
        ingress_from_resources = []
        ingress_from_al = []
        for resources in policy.get("from", {}).get("sources", {}).get("resources", []):
            tf_resources = self.tf_ref("projects/number", resources)
            ingress_from_resources.append(tf_resources)
        if ingress_from_resources:
            policy["from"]["sources"]["resources"] = ingress_from_resources
        for al in policy.get("from", {}).get("sources", {}).get("access_levels", []):
            tf_al = self.tf_ref("sc_access_level_name", al)
            ingress_from_al.append(tf_al)
        if ingress_from_al:
            policy["from"]["sources"]["access_levels"] = ingress_from_al

    for policy_name in ["ingress_policies", "egress_policies"]:
        for policy in data.get(policy_name, []):
            to_resources = []
            for resources in policy.get("to", {}).get("resources", []):
                tf_resources = self.tf_ref("projects/number", resources)
                to_resources.append(tf_resources)
            if to_resources:
                policy["to"]["resources"] = to_resources

    ScPerimeter(self, f"sc_perimiter_{name}", **data)


def create_sc_perimeter_bridge(self, data):
    """creates sc perimeter bridge"""
    name = data["perimeter_name"]
    data["description"] = (
        f'regular perimeter {name} {self.created["null"]["wait_for_members"].id}'
    )
    data["policy"] = self.tf_ref("sc_policy", data["policy"])
    ScPerimeterBridge(self, f"sc_bridge_{name}", **data)


def generate_sc_policy(self, my_resource, resource):
    """creates sc policy"""
    for data in self.eztf_config.get(my_resource, []):
        create_sc_policy(self, data)


def generate_sc_access_level(self, my_resource, resource):
    """creates sc access level"""
    depends_on = []
    for data in self.eztf_config.get(my_resource, []):
        create_sc_access_level(self, data)
        depends_on.append(f'${{module.sc_access_level_{data["name"]}}}')
    create_null_resource(self, depends_on)


def generate_sc_perimeter(self, my_resource, resource):
    """creates sc perimeter"""
    for data in self.eztf_config.get(my_resource, []):
        create_sc_perimeter(self, data)


def generate_sc_perimeter_bridge(self, my_resource, resource):
    """creates sc perimeter bridge"""
    for data in self.eztf_config.get(my_resource, []):
        create_sc_perimeter_bridge(self, data)
