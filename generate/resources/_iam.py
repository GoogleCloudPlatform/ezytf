from cdktf import (
    TerraformIterator,
    Token,
)
from imports.google.organization_iam_member import OrganizationIamMember
from imports.google.folder_iam_member import FolderIamMember
from imports.google.project_iam_member import ProjectIamMember
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
