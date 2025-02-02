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

from cdktf_cdktf_provider_google.iam_workforce_pool import (
    IamWorkforcePool,
    IamWorkforcePoolAccessRestrictionsAllowedServices,
)
from cdktf_cdktf_provider_google.iam_workforce_pool_provider import (
    IamWorkforcePoolProvider,
)
from cdktf_cdktf_provider_google.iam_workload_identity_pool import (
    IamWorkloadIdentityPool,
)
from cdktf_cdktf_provider_google.iam_workload_identity_pool_provider import (
    IamWorkloadIdentityPoolProvider,
    IamWorkloadIdentityPoolProviderX509TrustStoreTrustAnchors,
    IamWorkloadIdentityPoolProviderX509TrustStoreIntermediateCas,
)


def create_wif_pool(self, wif):
    """creates workforce pool"""
    name = wif["workforce_pool_id"]
    if not wif.get("parent"):
        wif["parent"] = f'organizations/{self.tf_ref("organization", "")}'

    if wif.get("access_restrictions", {}).get("allowed_services"):
        wif["access_restrictions"]["allowed_services"] = [
            IamWorkforcePoolAccessRestrictionsAllowedServices(**ar)
            for ar in wif["access_restrictions"]["allowed_services"]
        ]
    self.created["wif"][name] = IamWorkforcePool(self, f"wif_pool_{name}", **wif)


def create_wif_pool_provider(self, wif):
    """creates workforce pool provider"""
    name = wif["provider_id"]
    wif["workforce_pool_id"] = self.tf_ref("wif_pool", wif["workforce_pool_id"])

    self.created["wif"][name] = IamWorkforcePoolProvider(self, f"wif_pp_{name}", **wif)


def create_wi_pool(self, wi):
    """creates workload identity pool"""
    name = wi["workload_identity_pool_id"]
    wi["project"] = self.tf_ref("project", wi["project"])

    self.created["wi"][name] = IamWorkloadIdentityPool(self, f"wi_pool_{name}", **wi)


def create_wi_pool_provider(self, wi):
    """creates workload identity pool"""
    name = wi["workload_identity_pool_provider_id"]
    wi["workload_identity_pool_id"] = self.tf_ref(
        "wi_pool", wi["workload_identity_pool_id"]
    )
    wi["project"] = self.tf_ref("project", wi["project"])

    if wi.get("x509", {}).get("trust_store", {}).get("trust_anchors"):
        wi["x509"]["trust_store"]["trust_anchors"] = [
            IamWorkloadIdentityPoolProviderX509TrustStoreTrustAnchors(**ta)
            for ta in wi["x509"]["trust_store"]["trust_anchors"]
        ]
    if wi.get("x509", {}).get("trust_store", {}).get("intermediate_cas"):
        wi["x509"]["trust_store"]["intermediate_cas"] = [
            IamWorkloadIdentityPoolProviderX509TrustStoreIntermediateCas(**ta)
            for ta in wi["x509"]["trust_store"]["intermediate_cas"]
        ]

    self.created["wi"][name] = IamWorkloadIdentityPoolProvider(
        self, f"wi_pp_{name}", **wi
    )


def generate_wif_pool(self, my_resource, resource):
    """creates workforce pool"""
    for data in self.eztf_config.get(my_resource, []):
        create_wif_pool(self, data)


def generate_wif_pool_provider(self, my_resource, resource):
    """creates workforce pool provider"""
    for data in self.eztf_config.get(my_resource, []):
        create_wif_pool_provider(self, data)


def generate_wi_pool(self, my_resource, resource):
    """creates workload pool"""
    for data in self.eztf_config.get(my_resource, []):
        create_wi_pool(self, data)


def generate_wi_pool_provider(self, my_resource, resource):
    """creates workload pool"""
    for data in self.eztf_config.get(my_resource, []):
        create_wi_pool_provider(self, data)
