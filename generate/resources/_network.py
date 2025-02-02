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

from imports.network import Network
from imports.firewall_rules import FirewallRules
from imports.firewall_policy_nw import FirewallPolicyNw
from imports.firewall_policy_rh import FirewallPolicyRh
from imports.network_peering import NetworkPeering
from imports.cloud_router import CloudRouter
from imports.ff_net_vpc import FfNetVpc
from imports.ff_net_vpc_firewall import FfNetVpcFirewall
from imports.ff_net_firewall_policy import FfNetFirewallPolicy


import util


def create_network(self, vpc):
    vpc_name = vpc["network_name"]
    vpc["project_id"] = self.tf_ref("project", vpc["project_id"])

    self.created["network"][vpc_name] = Network(
        self,
        f"nw_{vpc_name}",
        **vpc,
    )


def create_firewall(self, fw):
    vpc_name = fw["network_name"]
    fw["project_id"] = self.tf_ref("project", fw["project_id"])
    fw["network_name"] = self.tf_ref("network", vpc_name)

    FirewallRules(
        self,
        f"fw_{vpc_name}",
        **fw,
    )


def create_fw_policy_rh(self, fp):
    node_type = self.which_node(fp["parent_node"])
    fp["parent_node"] = self.tf_ref(node_type, fp["parent_node"])
    if fp.get("target_org"):
        fp["target_org"] = self.tf_ref("organization", "/")

    fp["target_folders"] = [
        self.tf_ref("folder_id", fldr) for fldr in fp.get("target_folders", [])
    ]
    for rule in fp["rules"]:
        if rule.get("target_service_accounts"):
            rule["target_service_accounts"] = self.tf_ref(
                "service_accounts", rule["target_service_accounts"]
            )
    FirewallPolicyRh(
        self,
        f'fprh_{fp["policy_name"]}',
        **fp,
    )


def create_fw_policy_nw(self, fp):
    fp["project_id"] = self.tf_ref("project", fp["project_id"])
    fp["target_vpcs"] = [
        self.tf_ref("network_id", nw) for nw in fp.get("target_vpcs", [])
    ]
    for rule in fp["rules"]:
        if rule.get("target_service_accounts"):
            rule["target_service_accounts"] = self.tf_ref(
                "service_accounts", rule["target_service_accounts"]
            )
    FirewallPolicyNw(
        self,
        f'fpnw_{fp["policy_name"]}',
        **fp,
    )


def create_peering(self, pair, peer_module_depends_on):
    local, peer = pair["local_network"], pair["peer_network"]
    peer_name = f"peer_{local}_{peer}"
    pair["prefix"] = pair.get("prefix", "peer")
    pair["local_network"] = self.tf_ref("network", local)
    pair["peer_network"] = self.tf_ref("network", peer)
    pair["module_depends_on"] = peer_module_depends_on

    self.created["peering"][peer_name] = NetworkPeering(
        self,
        peer_name,
        **pair,
    )
    return [self.created["peering"][peer_name].complete_output]


def create_router(self, cr):
    vpc_name = cr["network"]
    region = cr["region"]
    vpc_re_name = f"{vpc_name}-{util.short_region(region)}"
    cr["name"] = f"cr-{vpc_re_name}"
    for nat in cr.get("nats"):
        nat["name"] = f"nat-{vpc_re_name}"
        for sub in nat.get("subnetworks", []):
            sub["name"] = self.tf_ref("subnet", sub["name"])
    cr["project"] = self.tf_ref("project", cr["project"])
    cr["network"] = self.tf_ref("network", vpc_name)

    CloudRouter(
        self,
        f"cr_{vpc_re_name}",
        **cr,
    )


def generate_networks(self, my_resource, resource):
    for vpc in self.eztf_config.get(my_resource, []):
        create_network(self, vpc)
    generate_routers(self, f"router_{my_resource}", "router")


def generate_firewalls(self, my_resource, resource):
    for fw in self.eztf_config.get(my_resource, []):
        create_firewall(self, fw)


def generate_peerings(self, my_resource, resource):
    peer_module_depends_on = []
    for pair in self.eztf_config.get(my_resource, []):
        peer_module_depends_on = create_peering(self, pair, peer_module_depends_on)


def generate_routers(self, my_resource, resource):
    self.file_seprator_variable(my_resource)
    for cr in self.eztf_config.get(my_resource, []):
        create_router(self, cr)


def add_subnets(self, my_resource, resource):
    self.added["subnets"] = self.added.get("subnets", {})
    for vpc in self.eztf_config.get(my_resource, []):
        for sub in vpc.get("subnets", []):
            region, subnet = sub["subnet_region"], sub["subnet_name"]
            self.added["subnets"][f"{region}/{subnet}"] = vpc["network_name"]


def generate_fw_policy_rh(self, my_resource, resource):
    for fw in self.eztf_config.get(my_resource, []):
        create_fw_policy_rh(self, fw)


def generate_fw_policy_nw(self, my_resource, resource):
    for fw in self.eztf_config.get(my_resource, []):
        create_fw_policy_nw(self, fw)


# Fabric


def create_ff_network(self, vpc):
    vpc_name = vpc["name"]
    vpc["project_id"] = self.tf_ref("project", vpc["project_id"])

    for subnet in vpc.get("subnets"):
        self.update_fabric_iam(subnet)

    for subnet in vpc.get("subnets_proxy_only"):
        self.update_fabric_iam(subnet)

    for subnet in vpc.get("subnets_psc"):
        self.update_fabric_iam(subnet)

    self.created["fabric"]["network"][vpc_name] = FfNetVpc(
        self,
        f"net_{vpc_name}",
        **vpc,
    )


def create_ff_vpc_firewall(self, fw):
    vpc_name = fw["network"]
    fw["project_id"] = self.tf_ref("project", fw["project_id"])
    fw["network_name"] = self.tf_ref("network", vpc_name)

    FfNetVpcFirewall(
        self,
        f"vpcfw_{vpc_name}",
        **fw,
    )


def create_ff_firewall_policy(self, fw):
    vpc_name = fw["name"]
    node_type = self.which_node(fw["parent_id"])

    fw["parent_id"] = self.tf_ref(node_type, fw["parent_id"])

    FfNetFirewallPolicy(
        self,
        f"fwpo_{vpc_name}",
        **fw,
    )


def generate_ff_network(self, my_resource, resource):
    for vpc in self.eztf_config.get(my_resource, []):
        create_ff_network(self, vpc)


def generate_ff_vpc_firewall(self, my_resource, resource):
    for fw in self.eztf_config.get(my_resource, []):
        create_ff_vpc_firewall(self, fw)


def generate_ff_firewall_policy(self, my_resource, resource):
    for fp in self.eztf_config.get(my_resource, []):
        create_ff_firewall_policy(self, fp)
