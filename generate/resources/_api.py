from cdktf import (
    TerraformIterator,
    Token,
)
from imports.google.project_service import ProjectService
from imports.project_services import ProjectServices


def enable_api(self, projects, api):
    api_projects = [self.tf_ref("project", project) for project in projects]
    iterator = TerraformIterator.from_list(api_projects)
    ProjectService(
        self,
        f"api_n_prj_{api}",
        for_each=iterator,
        service=api,
        disable_on_destroy=False,
        disable_dependent_services=False,
        project=Token.as_string(iterator.value),
    )


def create_project_services(self, api_svc):
    """creates project_services"""
    name = api_svc["project_id"]
    api_svc["project_id"] = self.tf_ref("project", api_svc["project_id"])

    ProjectServices(self, f"api_prj_{name}", **api_svc)


def generate_project_services(self, my_resource, resource):
    """creates project_services"""
    for data in self.eztf_config.get(my_resource, []):
        create_project_services(self, data)
