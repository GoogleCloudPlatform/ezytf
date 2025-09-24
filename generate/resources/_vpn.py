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

from cdktf_cdktf_provider_google.compute_external_vpn_gateway import (
    ComputeExternalVpnGateway,
    ComputeExternalVpnGatewayInterface,
)
from imports.vpn import Vpn
from imports.vpn_ha import VpnHa
from imports.ff_net_vpn_ha import FfNetVpnHa


def create_vpn(self, vpn):
    name = vpn["gateway_name"]
    vpn["network"] = self.tf_ref("network", vpn["network"])
    Vpn(self, f"vpn_{name}", **vpn)


def create_vpn_ha(self, vpn):
    name = vpn["name"]
    vpn["network"] = self.tf_ref("network", vpn["network"])
    if peer_gcp_gateway := vpn.get("peer_gcp_gateway"):
        vpn["peer_gcp_gateway"] = self.tf_ref("vpn_ha", peer_gcp_gateway)

    if not vpn.get("peer_external_gateway"):
        for _, tunnel in vpn.get("tunnels", {}).items():
            if peer_ext_link := tunnel.get("peer_external_gateway_self_link"):
                tunnel["peer_external_gateway_self_link"] = self.tf_ref(
                    "external_vpn_gateway", peer_ext_link
                )

    VpnHa(self, f"vpn_ha_{name}", **vpn)


def create_ext_vpn_gtw(self, ext_gtw):
    gtw_name = ext_gtw["name"]
    ext_gtw["interface"] = [
        ComputeExternalVpnGatewayInterface(**interface)
        for interface in ext_gtw["interface"]
    ]

    self.created["external_vpn_gateway"][gtw_name] = ComputeExternalVpnGateway(
        self, f"ext_vpn_gtw_{gtw_name}", **ext_gtw
    )


def generate_external_vpn_gateways(self, my_resource):
    self.created["external_vpn_gateway"] = self.created.get("external_vpn_gateway", {})
    for ext_gtw in self.eztf_config.get(my_resource, []):
        ext_gtw["project"] = self.tf_ref("project", ext_gtw["project"])
        create_ext_vpn_gtw(self, ext_gtw)


def generate_vpn(self, my_resource, resource):
    for vpn in self.eztf_config.get(my_resource, []):
        create_vpn(self, vpn)


def generate_vpn_ha(self, my_resource, resource):
    generate_external_vpn_gateways(self, f"external_vpn_gateway_{my_resource}")
    vpn_ha = self.eztf_config.get(my_resource, [])
    self.added["vpn_ha"] = self.added.get("vpn_ha", set())
    self.added["vpn_ha"].update({vpn["name"] for vpn in vpn_ha})
    for vpn in vpn_ha:
        create_vpn_ha(self, vpn)


# fabric


def create_ff_vpn_ha(self, vpn_ha):
    "create vpn_ha"
    vpn_ha_name = vpn_ha["name"]
    vpn_ha["project_id"] = self.tf_ref("project", vpn_ha["project_id"])
    vpn_ha["network"] = self.tf_ref("network", vpn_ha["network"])

    for _, peer in vpn_ha.get("peer_gateways", {}).items():
        if peer_gcp_gateway := peer.get("gcp"):
            peer["gcp"] = self.tf_ref("vpn_ha", peer_gcp_gateway)

    self.created["fabric"]["vpn_ha"][vpn_ha_name] = FfNetVpnHa(
        self, f"vpn_ha_{vpn_ha_name}", **vpn_ha
    )


def generate_ff_vpn_ha(self, my_resource, resource):
    "create vpn ha"
    for vpn_ha in self.eztf_config.get(my_resource, []):
        create_ff_vpn_ha(self, vpn_ha)
