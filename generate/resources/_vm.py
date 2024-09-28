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

from imports.google import compute_instance as ce
from imports.google.compute_disk import ComputeDisk, ComputeDiskGuestOsFeatures
from imports.instance_from_template import InstanceFromTemplate
from imports.instance_template import InstanceTemplate
from imports.mig import Mig
from imports.umig import Umig


def create_vm(self, vm):
    "create vm"
    vm_name = vm["name"]
    vm["project"] = self.tf_ref("project", vm["project"])
    if vm.get("service_account", {}).get("email"):
        vm["service_account"]["email"] = self.tf_ref(
            "service_account", vm["service_account"]["email"]
        )
    for disk in vm.get("attached_disk", []):
        if disk.get("source"):
            disk["source"] = self.tf_ref("disk", disk["source"])

    for ni in vm.get("network_interface", []):
        if ni.get("network"):
            ni["network"] = self.tf_ref("network", ni["network"])
        if ni.get("subnetwork"):
            ni["subnetwork"] = self.tf_ref("subnet", ni["subnetwork"])
        if ni.get("subnetwork_project"):
            ni["subnetwork_project"] = self.tf_ref("project", ni["subnetwork_project"])
        self.tf_param_list(
            ni, "alias_ip_range", ce.ComputeInstanceNetworkInterfaceAliasIpRange
        )
        self.tf_param_list(
            ni, "access_config", ce.ComputeInstanceNetworkInterfaceAccessConfig
        )
        self.tf_param_list(
            ni, "ipv6_access_config", ce.ComputeInstanceNetworkInterfaceIpv6AccessConfig
        )

    self.tf_param_list(vm, "network_interface", ce.ComputeInstanceNetworkInterface)
    self.tf_param_list(vm, "scratch_disk", ce.ComputeInstanceScratchDisk)
    self.tf_param_list(vm, "attached_disk", ce.ComputeInstanceAttachedDisk)
    self.tf_param_list(vm, "guest_accelerator", ce.ComputeInstanceGuestAccelerator)
    self.tf_param_list(
        vm.get("scheduling"),
        "node_affinities",
        ce.ComputeInstanceSchedulingNodeAffinities,
    )
    self.tf_param_list(
        vm, "scheduling_node_affinities", ce.ComputeInstanceSchedulingNodeAffinities
    )

    self.created["vm"][vm_name] = ce.ComputeInstance(self, f"vm_{vm_name}", **vm)


def create_disk(self, disk):
    "create disk"
    disk_name = disk["name"]
    disk["project"] = self.tf_ref("project", disk["project"])

    self.tf_param_list(disk, "guest_os_features", ComputeDiskGuestOsFeatures)

    self.created["disk"][disk_name] = ComputeDisk(self, f"disk_{disk_name}", **disk)


def create_instance_template(self, cit):
    "create instance template"
    cit_name = cit["name_prefix"]
    cit["project_id"] = self.tf_ref("project", cit["project_id"])
    if cit.get("service_account", {}).get("email"):
        cit["service_account"]["email"] = self.tf_ref(
            "service_account", cit["service_account"]["email"]
        )
    if cit.get("network"):
        cit["network"] = self.tf_ref("network", cit["network"])
    if cit.get("subnetwork"):
        cit["subnetwork"] = self.tf_ref("subnet", cit["subnetwork"])
    if cit.get("subnetwork_project"):
        cit["subnetwork_project"] = self.tf_ref("project", cit["subnetwork_project"])
    self.created["vm_template"][cit_name] = InstanceTemplate(
        self, f"vm_tmpl_{cit_name}", **cit
    )


def create_instance_from_template(self, ift):
    "create instance from template"
    ift_name = ift["hostname"]
    if ift.get("network"):
        ift["network"] = self.tf_ref("network", ift["network"])
    if ift.get("subnetwork"):
        ift["subnetwork"] = self.tf_ref("subnet", ift["subnetwork"])
    if ift.get("subnetwork_project"):
        ift["subnetwork_project"] = self.tf_ref("project", ift["subnetwork_project"])
    ift["instance_template"] = self.tf_ref("vm_template", ift["instance_template"])
    self.created["vm_from_template"][ift_name] = InstanceFromTemplate(
        self, f"vmft_{ift_name}", **ift
    )


def create_mig(self, mig):
    "create mig"
    mig_name = mig["mig_name"]
    mig["project_id"] = self.tf_ref("project", mig["project_id"])
    mig["instance_template"] = self.tf_ref("vm_template", mig["instance_template"])
    self.created["mig"][mig_name] = Mig(self, f"mig_{mig_name}", **mig)


def create_umig(self, umig):
    "create umig"
    umig_name = umig["hostname"]
    umig["project_id"] = self.tf_ref("project", umig["project_id"])
    if umig.get("network"):
        umig["network"] = self.tf_ref("network", umig["network"])
    if umig.get("subnetwork"):
        umig["subnetwork"] = self.tf_ref("subnet", umig["subnetwork"])
    if umig.get("subnetwork_project"):
        umig["subnetwork_project"] = self.tf_ref("project", umig["subnetwork_project"])
    umig["instance_template"] = self.tf_ref("vm_template", umig["instance_template"])
    self.created["umig"][umig_name] = Umig(self, f"umig_{umig_name}", **umig)


def generate_compute_instances(self, my_resource, resource):
    "create compute instance"
    for vm in self.eztf_config.get(my_resource, []):
        create_vm(self, vm)


def generate_compute_disk(self, my_resource, resource):
    "create compute disk"
    for disk in self.eztf_config.get(my_resource, []):
        create_disk(self, disk)


def generate_instance_from_template(self, my_resource, resource):
    "create instance"
    for vm in self.eztf_config.get(my_resource, []):
        create_instance_from_template(self, vm)


def generate_instance_template(self, my_resource, resource):
    "create instance template"
    for vm in self.eztf_config.get(my_resource, []):
        create_instance_template(self, vm)


def generate_mig(self, my_resource, resource):
    "create mig"
    for vm in self.eztf_config.get(my_resource, []):
        create_mig(self, vm)


def generate_umig(self, my_resource, resource):
    "create umig"
    for vm in self.eztf_config.get(my_resource, []):
        create_umig(self, vm)
