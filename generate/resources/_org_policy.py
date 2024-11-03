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
    TerraformLocal,
)
from imports.org_policy_v2 import OrgPolicyV2
from cdktf_cdktf_provider_google.org_policy_custom_constraint import (
    OrgPolicyCustomConstraint,
)
import util


def create_org_policy(self, org_policy):
    node_type = org_policy["policy_root"]
    node = org_policy.get("policy_root_id", "org")
    name = org_policy["constraint"]
    org_policy["policy_root_id"] = self.tf_ref(node_type, node)
    org_policy["constraint"] = self.tf_ref("custom_org_policy", name)

    OrgPolicyV2(
        self,
        f"org_policy_{name}_{node_type}_{util.clean_tf_folder(node)}",
        **org_policy,
    )


def create_custom_org_policy(self, c_org_policy):
    org_policy = {
        "constraint": c_org_policy["name"],
        "policy_type": "boolean",
        "policy_root": c_org_policy["policy_root"],
        "policy_root_id": c_org_policy.get("policy_root_id", "org"),
        "rules": [{"enforcement": True, "allow": [], "deny": [], "conditions": []}],
    }
    del c_org_policy["policy_root"]
    del c_org_policy["policy_root_id"]

    name = c_org_policy["name"]
    c_org_policy["parent"] = f'organizations/{self.tf_ref("organization", "")}'

    self.created["custom_org_policy"][name] = OrgPolicyCustomConstraint(
        self,
        f"c_org_policy_{name}",
        **c_org_policy,
    )
    create_org_policy(self, org_policy)


def generate_org_policies(self, my_resource, resource):
    self.ensure_data(["google_org"])
    for org_policy in self.eztf_config.get(my_resource, []):
        name = org_policy["constraint"]
        if name == "iam.allowedPolicyMemberDomains":
            org_allow_domain = org_policy["rules"][0]["allow"]
            org_allow_domain.append(
                self.created["data"]["google_org"].directory_customer_id
            )
            org_policy["rules"][0]["allow"] = TerraformLocal(
                self,
                "org_allow_member_domain",
                org_allow_domain,
            ).as_list

        create_org_policy(self, org_policy)


def generate_custom_org_policies(self, my_resource, resource):
    self.ensure_data(["google_org"])
    for custom_org_policy in self.eztf_config.get(my_resource, []):
        create_custom_org_policy(self, custom_org_policy)
