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

from imports.kms import Kms


def create_kms(self, kms):
    """creates sc access level"""
    name = kms["keyring"]
    kms["project_id"] = self.tf_ref("project", kms["project_id"])
    owners = []
    for owner in kms.get("owners", []):
        subowners = []
        for principal in owner.split(","):
            principal = principal.strip().split(":")
            p_type, principal_id = principal[0], principal[1]
            principal_id = self.tf_ref(p_type.lower(), principal_id)
            new_principal = f"{p_type}:{principal_id}"
            subowners.append(new_principal)
        subowners = ",".join(subowners)
        owners.append(subowners)
    if owners:
        kms["owners"] = owners
    self.created["kms"][name] = Kms(self, f"kms_{name}", **kms)


def generate_kms(self, my_resource, resource):
    """creates sc perimeter"""
    for data in self.eztf_config.get(my_resource, []):
        create_kms(self, data)
