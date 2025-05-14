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

import re
from typing import Any
from constructs import Construct
from cdktf import (
    TerraformStack,
    TerraformVariable,
    GcsBackend,
)
from cdktf_cdktf_provider_google.provider import GoogleProvider
import util
from ._users import generate_users
from ._group import generate_groups, generate_ff_groups
from ._org import generate_ff_orgs
from ._wif import (
    generate_wif_pool,
    generate_wi_pool,
    generate_wif_pool_provider,
    generate_wi_pool_provider,
)
from ._sa import generate_sa, generate_ff_iam_sa
from ._myfolders import generate_folders, generate_ff_folders
from ._projects import generate_projects, generate_svc_projects, generate_ff_projects
from ._iam import generate_iam
from ._api import generate_project_services
from ._network import (
    generate_networks,
    generate_peerings,
    generate_firewalls,
    generate_routers,
    add_subnets,
    generate_fw_policy_nw,
    generate_fw_policy_rh,
    generate_ff_network,
    generate_ff_vpc_firewall,
    generate_ff_firewall_policy,
)
from ._networking import (
    generate_ff_swp,
    generate_ff_dns,
    generate_ff_dnspo,
    generate_ff_addr,
    generate_ff_nat,
)
from ._logging import (
    generate_logging,
    generate_log_destination,
    generate_logsink,
    add_dest_sink_map,
    generate_ff_logbucket,
)
from ._monitoring import generate_monitoring
from ._org_policy import generate_org_policies, generate_custom_org_policies

from ._pubsub import generate_ff_pubsub
from ._gke import generate_gke
from ._mydata import data_google_org
from ._kms import generate_kms, generate_ff_kms
from ._gcs import generate_gcs, generate_ff_gcs
from ._vpn import (
    generate_vpn,
    generate_vpn_ha,
    generate_external_vpn_gateways,
    generate_ff_vpn_ha,
)
from ._vm import (
    generate_compute_disk,
    generate_compute_instances,
    generate_instance_from_template,
    generate_instance_template,
    generate_mig,
    generate_umig,
    generate_ff_vm,
)
from ._database import generate_cloudsql
from ._bigquery import (
    generate_bigquery_dataset,
    generate_bigquery_table,
    generate_bigquery_routine,
)
from ._vpcsc import (
    generate_sc_policy,
    generate_sc_access_level,
    generate_sc_perimeter,
    generate_sc_perimeter_bridge,
)
from ._certificate import generate_ff_cas, generate_ff_cm
from ._parallelstore import generate_parallelstore
from ._any_module import generate_any_module
from ._any_data import generate_any_data
from ._any_resource import generate_any_resource


creation = {
    "users": generate_users,
    "groups": generate_groups,
    "ff_groups": generate_ff_groups,
    "ff_orgs": generate_ff_orgs,
    "wif_pool": generate_wif_pool,
    "wi_pool": generate_wi_pool,
    "wif_pool_provider": generate_wif_pool_provider,
    "wi_pool_provider": generate_wi_pool_provider,
    "folders": generate_folders,
    "projects": generate_projects,
    "ff_folders": generate_ff_folders,
    "ff_projects": generate_ff_projects,
    "iam": generate_iam,
    "service_account": generate_sa,
    "ff_iam_sa": generate_ff_iam_sa,
    "project_api": generate_project_services,
    "network": generate_networks,
    "ff_network": generate_ff_network,
    "ff_vpc_firewall": generate_ff_vpc_firewall,
    "ff_firewall_policy": generate_ff_firewall_policy,
    "firewall": generate_firewalls,
    "firewall_policy_nw": generate_fw_policy_nw,
    "firewall_policy_rh": generate_fw_policy_rh,
    "ff_swp": generate_ff_swp,
    "ff_dns": generate_ff_dns,
    "ff_dnspo": generate_ff_dnspo,
    "ff_addr": generate_ff_addr,
    "ff_nat": generate_ff_nat,
    "_svc_projects": generate_svc_projects,
    "peering": generate_peerings,
    "router": generate_routers,
    "logging": generate_logging,
    "logsink": generate_logsink,
    "logpubsub": generate_log_destination,
    "logstorage": generate_log_destination,
    "logbucket": generate_log_destination,
    "logbigquery": generate_log_destination,
    "logproject": generate_log_destination,
    "ff_logbucket": generate_ff_logbucket,
    "monitoring": generate_monitoring,
    "pubsub": generate_ff_pubsub,
    "org_policy": generate_org_policies,
    "org_node_policy": generate_org_policies,
    "custom_org_policy": generate_custom_org_policies,
    "external_vpn_gateway": generate_external_vpn_gateways,
    "vpn": generate_vpn,
    "vpn_ha": generate_vpn_ha,
    "ff_vpn_ha": generate_ff_vpn_ha,
    "gke": generate_gke,
    "gke_private": generate_gke,
    "gke_autopilot": generate_gke,
    "gke_autopilot_private": generate_gke,
    "kms": generate_kms,
    "ff_kms": generate_ff_kms,
    "ff_cas": generate_ff_cas,
    "ff_cm": generate_ff_cm,
    "sc_policy": generate_sc_policy,
    "sc_access_level": generate_sc_access_level,
    "sc_perimeter": generate_sc_perimeter,
    "sc_perimeter_bridge": generate_sc_perimeter_bridge,
    "gcs": generate_gcs,
    "ff_gcs": generate_ff_gcs,
    "cloudsql": generate_cloudsql,
    "pgsql": generate_cloudsql,
    "mysql": generate_cloudsql,
    "mssql": generate_cloudsql,
    "vm": generate_compute_instances,
    "vm_template": generate_instance_template,
    "vm_from_template": generate_instance_from_template,
    "ff_vm": generate_ff_vm,
    "mig": generate_mig,
    "umig": generate_umig,
    "disk": generate_compute_disk,
    "bq_dataset": generate_bigquery_dataset,
    "bq_table": generate_bigquery_table,
    "bq_routine": generate_bigquery_routine,
    "any_module": generate_any_module,
    "mod": generate_any_module,
    "any_resource": generate_any_resource,
    "res": generate_any_resource,
    "any_data": generate_any_data,
    "data": generate_any_data,
    "parallelstore": generate_parallelstore,
}

data_creation = {"google_org": data_google_org}

variable_creation = {
    "users": ["organization_id", "setup_service_account"],
    "iam": ["organization_id"],
    "folders": ["organization_id"],
    "projects": ["organization_id", "billing_id", "project_suffix"],
    "firewall_policy_nw": ["organization_id"],
    "firewall_policy_rh": ["organization_id"],
    "org_policy": ["organization_id"],
    "custom_org_policy": ["organization_id"],
    "logging": ["organization_id"],
    "logsink": ["organization_id"],
    "sc_policy": ["organization_id"],
}

added_ref = {"network": [add_subnets], "logsink": [add_dest_sink_map]}

sentinel = object()


class MyStack(TerraformStack):
    """Creates GCP tf"""

    def __init__(
        self,
        scope: Construct,
        id: str,
        eztf_config: Any,
        sub_stack_name: str,
        eztf_range_resources: Any,
    ):
        super().__init__(scope, id)
        self.eztf_config = eztf_config
        self.created = {
            "vars": {},
            "locals": {},
            "data": {},
            "resource": {},
            "null": {},
        }
        self.added = {}
        self.tf_vars = {}
        self.provided_vars = eztf_config.get("variable", {})

        self._create_backend(sub_stack_name)
        self.file_seprator_variable("variables", True)

        for range_resource in eztf_range_resources:
            for my_resource, resource in range_resource.items():
                if resource == "variable" or resource == "tf_vars":
                    all_stack_vars = self.eztf_config.get(my_resource,{})
                    stack_vars = util.dict_without_prefixes(all_stack_vars, ["setup_", "ez_"])
                    self.provided_vars.update(all_stack_vars)
                    self._create_variables(stack_vars)
        
        for range_resource in eztf_range_resources:
            for my_resource, resource in range_resource.items():
                if not creation.get(resource):
                    continue
                if not self.created.get(resource):
                    self.created[resource] = {}
                if added_ref.get(resource):
                    for add_ref in added_ref[resource]:
                        add_ref(self, my_resource, resource)
                if variable_creation.get(resource):
                    self.ensure_variables(variable_creation[resource])

        for range_resource in eztf_range_resources:
            for my_resource, resource in range_resource.items():
                if creation.get(resource):
                    self.file_seprator_variable(my_resource)
                    creation[resource](self, my_resource, resource)

    def file_seprator_variable(self, name, force=False):
        if self.eztf_config.get(name) or force:
            TerraformVariable(self, f"{util.RANDOM_WORD}file_{name}")

    def _create_backend(self, config_sub_type):
        var = self.eztf_config.get("variable", {})

        GoogleProvider(self, id="google", project=var.get("setup_project_id"))
        if var.get("setup_gcs"):
            GcsBackend(
                self,
                bucket=var.get("setup_gcs"),
                prefix=f"terraform-{config_sub_type}-state",
            )

    def ensure_data(self, data_li):
        for name in data_li:
            if not self.created["data"].get(name):
                data_creation[name](self)

    def ensure_variables(self, variables):
        self._create_variables({variable: self.provided_vars.get(variable,"") for variable in variables})

    def _create_variables(self, variables):
        if not self.created.get("vars"):
            self.created["vars"] = {}
        for variable, value in variables.items():
            if not self.created["vars"].get(variable):
                self.created["vars"][variable] = TerraformVariable(
                    self,
                    variable,
                    description=" ".join(variable.split("_")),
                )
                self.tf_vars[variable] = value

    def ref_principal(self, name):
        p = name.split(":")
        p_type, p_id = p[0], ":".join(p[1:])
        ref_p_id = self.tf_ref(p_type.lower(), p_id)
        return f"{p_type}:{ref_p_id}"

    def _re_prj_region_subnet(self, subnet_link):
        pattern = r"projects/(.+)/regions/(.+)/subnetworks/(.+)"
        sub_li = subnet_link.split("/")
        if match := re.search(pattern, subnet_link):
            return match.group(1), match.group(2), match.group(3)
        elif len(sub_li) == 3:
            return sub_li[0], sub_li[1], sub_li[2]
        elif len(sub_li) == 2:
            return None, sub_li[0], sub_li[1]
        return None, None, None

    def update_fabric_iam(self, dic):
        for key, values in dic.get("iam_bindings_additive", {}).items():
            principal_ref = self.ref_principal(values.get("member"))
            dic["iam_bindings_additive"][key]["member"] = principal_ref

        for key, values in dic.get("iam_bindings", {}).items():
            principal_ref = self.ref_principal(values.get("member"))
            dic["iam_bindings"][key]["member"] = principal_ref

        for role, principal_list in dic.get("iam", {}).items():
            principal_ref = [
                self.ref_principal(principal) for principal in principal_list
            ]
            dic["iam"][role] = principal_ref

        iam_by_principals = {}
        for principal, role_list in dic.get("iam_by_principals", {}).items():
            principal_ref = self.ref_principal(principal)
            iam_by_principals[principal_ref] = role_list

        if dic.get("iam_by_principals"):
            dic["iam_by_principals"] = iam_by_principals

        iam_by_principals_additive = {}
        for principal, role_list in dic.get("iam_by_principals_additive", {}).items():
            principal_ref = self.ref_principal(principal)
            iam_by_principals_additive[principal_ref] = role_list

        if dic.get("iam_by_principals_additive"):
            dic["iam_by_principals_additive"] = iam_by_principals_additive

    def which_node(self, node):
        if not node or node == "/" or node.startswith("organizations/"):
            return "organization"
        if node.startswith("/") or node.startswith("folders/"):
            return "folder"
        return "project"

    def resource_function(self, resource: str, nested_params=None, provider=""):
        res_name = resource
        if not provider:
            provider = resource.split("_")[0]
            res_name = "_".join(resource.split("_")[1:])
        if nested_params:
            res_name = "_".join([res_name] + nested_params)
        method_name = util.pascal_case(res_name)
        module = __import__(
            f"cdktf_cdktf_provider_{provider}.{res_name}", fromlist=[res_name]
        )
        func = getattr(module, method_name)
        return func, res_name

    def tf_param_list(self, data, key, attribute_object_func):
        if data and data.get(key):
            data[key] = [attribute_object_func(**item) for item in data[key]]

    def tf_parameters_list(self, data, resource, nested_params):
        attribute_func, _ = self.resource_function(
            resource, nested_params, provider="google"
        )
        self.tf_param_list(self, data, nested_params[-1], attribute_func)

    # fmt: off
    def tf_ref(self, res_type, name, default=sentinel):
        if default is sentinel:
            default = name
        refname = default
        if (res_type == "billing" or res_type == "billing_account") and not name:
            self.ensure_variables(["billing_id"])
            refname = self.created["vars"]["billing_id"].string_value
        if res_type == "customer_id" and not name:
            if self.created.get("data", {}).get("google_org"):
                refname = self.created["data"]["google_org"].directory_customer_id
            else:
                self.ensure_variables(["customer_id"])
                refname = self.created["vars"]["customer_id"].string_value
        if res_type == "user" and self.created.get("users", {}).get(name):
            refname = self.created["users"][name].primary_email
        if res_type == "group" and self.created.get("groups", {}).get(name):
            refname = self.created["groups"][name].id_output
        if res_type == "group_name" and self.created.get("groups", {}).get(name):
            refname = self.created["groups"][name].name_output
        if (res_type == "service_account" or res_type == "serviceaccount") and self.created.get("service_account", {}).get(name):
            refname = self.created["service_account"][name].email
        elif res_type == "network" and self.created.get("network", {}).get(name):
            refname = self.created["network"][name].network_self_link_output
        elif res_type == "network_name" and self.created.get("network", {}).get(name):
            refname = self.created["network"][name].network_name_output
        elif res_type == "network_id" and self.created.get("network", {}).get(name):
            refname = self.created["network"][name].network_id_output
        elif res_type == "project" and self.created.get("projects", {}).get(name):
            refname = self.created["projects"][name].project_id_output
        elif res_type == "project_number" and self.created.get("projects", {}).get(name):
            refname = self.created["projects"][name].project_number_output
        elif res_type == "projects/number" and self.created.get("projects", {}).get(name):
            refname = f'projects/{self.created["projects"][name].project_number_output}'
        elif res_type == "organization":
            self.ensure_variables(["organization_id"])
            refname = self.created["vars"]["organization_id"].string_value
        elif res_type == "folder" and self.created.get("folders", {}).get(name):
            refname = self.created["folders"][name].name
        elif res_type == "folder_id" and self.created.get("folders", {}).get(name):
            refname = self.created["folders"][name].folder_id
        elif res_type == "subnet":
            prj, region, subnet = self._re_prj_region_subnet(name)
            region_subnet = f"{region}/{subnet}"
            if vpc_name := self.added.get("subnets", {}).get(region_subnet):
                refname = f'${{module.nw_{vpc_name}.subnets["{region_subnet}"].self_link}}'
            elif region and subnet:
                prj = prj or '${var.nw_project_id}'
                refname = f"projects/{prj}/regions/{region}/subnetworks/{subnet}"
        elif res_type == "vpn_ha" and name in self.added.get("vpn_ha", set()):
            refname = f"${{module.vpn_ha_{name}.self_link}}"
        elif res_type == "external_vpn_gateway" and self.created.get("external_vpn_gateway", {}).get(name):
            refname = self.created["external_vpn_gateway"][name].self_link
        elif res_type == "sc_policy" and self.created.get("sc_policy", {}).get(name):
            refname = self.created["sc_policy"][name].name
        elif res_type == "sc_access_level_name" and self.created.get("sc_access_level", {}).get(name):
            refname = self.created["sc_access_level"][name].name_output
        elif res_type == "custom_org_policy" and self.created.get("custom_org_policy", {}).get(name):
            refname = self.created["custom_org_policy"][name].name
        elif res_type == "log_destination" and self.created.get(res_type, {}).get(name):
            refname = self.created[res_type][name].destination_uri_output
        if res_type == "vm_template" and self.created.get("vm_template", {}).get(name):
            refname = self.created["vm_template"][name].self_link_unique_output
        if res_type == "disk" and self.created.get("disk", {}).get(name):
            refname = self.created["disk"][name].self_link
        if res_type == "bq_dataset" and self.created.get("bq_dataset", {}).get(name):
            refname = self.created["bq_dataset"][name].dataset_id
        if res_type == "bq_table" and self.created.get("bq_table", {}).get(name):
            refname = self.created["bq_table"][name].table_id
        if res_type == "bq_routine" and self.created.get("bq_routine", {}).get(name):
            refname = self.created["bq_routine"][name].routine_id
        if res_type == "wif_pool" and self.created.get("wif_pool", {}).get(name):
            refname = self.created["wif_pool"][name].workforce_pool_id
        if res_type == "wi_pool" and self.created.get("wi_pool", {}).get(name):
            refname = self.created["wi_pool"][name].workload_identity_pool_id
        if res_type == "cx" and self.created.get("cx", {}).get(name):
            refname = self.created["cx"][name].id
        if res_type == "datastore" and self.created.get("datastore", {}).get(name):
            refname = self.created["datastore"][name].data_store_id
        if res_type == "ai_index" and self.created.get("ai_index", {}).get(name):
            refname = self.created["ai_index"][name].id
        if res_type == "ai_index_endpoint" and self.created.get("ai_index_endpoint", {}).get(name):
            refname = self.created["ai_index_endpoint"][name].id
        return refname
    # fmt: on
