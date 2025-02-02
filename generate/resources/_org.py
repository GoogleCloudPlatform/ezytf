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


from imports.ff_organization import FfOrganization


def create_ff_org(self, org):
    org_id = org.get("organization_id", "org")
    org["organization_id"] = self.tf_ref("organization", "")

    self.update_fabric_iam(org)
    for _, values in org.get("tags", {}).items():
        self.update_fabric_iam(values)
        for _, tagvalues in values.get("values", {}).items():
            self.update_fabric_iam(tagvalues)

    self.created["fabric_org"][org_id] = FfOrganization(self, f"org_{org_id}", **org)


def generate_ff_orgs(self, my_resource, resource):
    for org in self.eztf_config.get(my_resource, []):
        create_ff_org(self, org)
