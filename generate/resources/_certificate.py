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

from imports.ff_certificate_authority_service import FfCertificateAuthorityService
from imports.ff_certificate_manager import FfCertificateManager


def create_ff_cas(self, cas):
    """creates cas"""
    name = cas["ca_pool_config"].get("name", cas["ca_pool_config"]["ca_pool_id"])
    cas["project_id"] = self.tf_ref("project", cas["project_id"])

    self.update_fabric_iam(cas)

    self.created["fabric"]["cas"][name] = FfCertificateAuthorityService(
        self, f"cas_{name}", **cas
    )


def generate_ff_cas(self, my_resource, resource):
    """creates cas"""
    for data in self.eztf_config.get(my_resource, []):
        create_ff_cas(self, data)


def create_ff_cm(self, cm):
    """creates cm"""
    name = cm["project_id"]
    cm["project_id"] = self.tf_ref("project", cm["project_id"])

    self.created["fabric"]["cm"][name] = FfCertificateManager(self, f"cm_{name}", **cm)


def generate_ff_cm(self, my_resource, resource):
    """creates cm"""
    for data in self.eztf_config.get(my_resource, []):
        create_ff_cm(self, data)
