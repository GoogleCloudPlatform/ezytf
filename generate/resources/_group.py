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


from imports.group import Group
from imports.ff_cloud_identity_group import FfCloudIdentityGroup


def remove_group_member_overlap(group):
    group_owners = set(group.get("owners", []))
    group_managers = set(group.get("managers", []))
    group_members = set(group.get("members", []))
    group_managers = group_managers - group_owners
    group_members = group_members - group_managers - group_owners
    if group.get("owners"):
        group["owners"] = list(group_owners)
    if group.get("managers"):
        group["managers"] = list(group_managers)
    if group.get("members"):
        group["members"] = list(group_members)


def create_group(self, group):
    group_id = group["id"]
    remove_group_member_overlap(group)
    for role in ["owners", "managers", "members"]:
        if group.get(role):
            group[role] = [self.tf_ref("user", user) for user in group[role]]
    self.created["groups"][group_id] = Group(
        self,
        f"grp_{group_id}",
        **group,
    )


def generate_groups(self, my_resource, resource):
    for group in self.eztf_config.get(my_resource, []):
        remove_group_member_overlap(group)
        create_group(self, group)


def create_ff_group(self, group):
    group_id = group["name"]
    if not group.get("customer_id"):
        group["customer_id"] = f"customers/{self.eztf_config.get('customer_id')}"
    remove_group_member_overlap(group)
    for role in ["managers", "members"]:
        if group.get(role):
            group[role] = [self.tf_ref("user", user) for user in group[role]]
    self.created["groups"][group_id] = FfCloudIdentityGroup(
        self,
        f"grp_{group_id}",
        **group,
    )


def generate_ff_groups(self, my_resource, resource):
    self.ensure_data(["google_org"])
    for group in self.eztf_config.get(my_resource, []):
        group = remove_group_member_overlap(group)
        create_group(self, group)
