from imports.ff_net_swp import FfNetSwp
from imports.ff_dns import FfDns
from imports.ff_dns_response_policy import FfDnsResponsePolicy
from imports.ff_net_cloudnat import FfNetCloudnat
from imports.ff_net_address import FfNetAddress




def create_ff_swp(self, swp):
    swp_name = swp["name"]
    swp["project_id"] = self.tf_ref("project", swp["project_id"])
    swp["network"] = self.tf_ref("network", swp["network"])
    swp["subnetwork"] = self.tf_ref("subnet", swp["subnetwork"])
    if swp.get("certificates"):
        swp["certificates"] = [
            self.tf_ref("certificate", cert) for cert in swp.get("certificates", [])
        ]
    if swp.get("service_attachment", {}).get("nat_subnets"):
        swp["service_attachment"]["nat_subnets"] = [
            self.tf_ref("subnet", nat_sub)
            for nat_sub in swp["service_attachment"]["nat_subnets"]
        ]

    self.created["fabric"]["swp"][swp_name] = FfNetSwp(
        self,
        f"swp_{swp_name}",
        **swp,
    )


def generate_ff_swp(self, my_resource, resource):
    for swp in self.eztf_config.get(my_resource, []):
        create_ff_swp(self, swp)


def create_ff_dns(self, dns):
    dns_name = dns["name"]
    dns["project_id"] = self.tf_ref("project", dns["project_id"])

    for key in ["forwarding", "peering", "private"]:
        if dns.get("zone_config", {}).get(key, {}).get("client_networks"):
            dns["zone_config"][key]["client_networks"] = [
                self.tf_ref("network", vpc)
                for vpc in dns["zone_config"][key]["client_networks"]
            ]
    if dns.get("zone_config", {}).get("peering", {}).get("peer_network"):
        dns["zone_config"]["peering"]["peer_network"] = self.tf_ref(
            "network", dns["zone_config"]["peering"]["peer_network"]
        )

    self.update_fabric_iam(dns)

    self.created["fabric"]["dns"][dns_name] = FfDns(
        self,
        f"dns_{dns_name}",
        **dns,
    )


def generate_ff_dns(self, my_resource, resource):
    for dns in self.eztf_config.get(my_resource, []):
        create_ff_dns(self, dns)


def create_ff_dnspo(self, dnspo):
    dnspo_name = dnspo["name"]
    dnspo["project_id"] = self.tf_ref("project", dnspo["project_id"])

    for name, vpc in dnspo.get("networks", {}).items():
        dnspo["networks"][name] = self.tf_ref("network", vpc)

    self.created["fabric"]["dns_policy"][dnspo_name] = FfDnsResponsePolicy(
        self,
        f"dnspo_{dnspo_name}",
        **dnspo,
    )


def generate_ff_dnspo(self, my_resource, resource):
    for dnspo in self.eztf_config.get(my_resource, []):
        create_ff_dnspo(self, dnspo)


def create_ff_addr(self, addr):
    addr_name = addr["name"]
    addr["project_id"] = self.tf_ref("project", addr["project_id"])

    for key in [
        "external_addresses",
        "internal_addresses",
        "global_addresses",
        "ipsec_interconnect_addresses",
        "network_attachments",
        "psa_addresses",
        "psc_addresses",
    ]:
        if not addr.get(key):
            continue
        for ref_name, ref_type in [
            ("network", "network"),
            ("subnetwork", "subnet"),
            ("subnet_self_link", "subnet"),
        ]:
            if addr[key].get(ref_name):
                addr[key][ref_name] = self.tf_ref(ref_type, addr[key][ref_name])

    self.created["fabric"]["address"][addr_name] = FfNetAddress(
        self,
        f"addr_{addr_name}",
        **addr,
    )


def generate_ff_addr(self, my_resource, resource):
    for addr in self.eztf_config.get(my_resource, []):
        create_ff_addr(self, addr)


def create_ff_nat(self, nat):
    nat_name = nat["name"]
    nat["project_id"] = self.tf_ref("project", nat["project_id"])

    if nat.get("router_network"):
        nat["router_network"] = self.tf_ref("network", nat["router_network"])

    for sub in nat.get("config_source_subnetworks", {}).get("subnetworks", []):
        if sub.get("self_link"):
            sub["self_link"] = self.tf_ref("subnet", sub["self_link"])

    if nat.get("addresses"):
        nat["addresses"] = [
            self.tf_ref("address", addr) for addr in nat.get["addresses"]
        ]

    self.created["fabric"]["nat"][nat_name] = FfNetCloudnat(
        self,
        f"nat_{nat_name}",
        **nat,
    )


def generate_ff_nat(self, my_resource, resource):
    for nat in self.eztf_config.get(my_resource, []):
        create_ff_nat(self, nat)



