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

from cdktf import (
    TerraformIterator,
    Token,
)
from cdktf_cdktf_provider_google.organization_iam_member import OrganizationIamMember
from cdktf_cdktf_provider_google.folder_iam_member import FolderIamMember
from cdktf_cdktf_provider_google.project_iam_member import ProjectIamMember
import util


def create_iam_members(self, node, principal, roles):
    iterator = TerraformIterator.from_list(roles)
    tf_access_id = util.clean_principal_id(principal)
    node_type = self.which_node(node)
    principal_ref = self.ref_principal(principal)

    iam_params = {
        "for_each": iterator,
        "role": Token.as_string(iterator.value),
        "member": principal_ref,
    }

    if node_type == "project":
        ProjectIamMember(
            self,
            f"prj_iam_{node}_{tf_access_id}",
            project=self.tf_ref("project", node),
            **iam_params,
        )
    elif node_type == "folder":
        FolderIamMember(
            self,
            f"fldr_iam_{util.clean_tf_folder(node)}_{tf_access_id}",
            folder=self.tf_ref("folder", node),
            **iam_params,
        )
    elif node_type == "organization":
        OrganizationIamMember(
            self,
            f"org_iam_{tf_access_id}",
            org_id=self.tf_ref("organization", "/"),
            **iam_params,
        )


def generate_iam(self, my_resource, resource):
    for node, principal_roles in self.eztf_config.get(my_resource, {}).items():
        for principal, roles in principal_roles.items():
            create_iam_members(self, node, principal, roles)

def generate_iam_member(self, my_resource, resource):
    for iam in self.eztf_config.get(my_resource, {}).items():
        create_iam_members(self, iam.get("node"), iam.get("principal"), iam.get("roles"))