from imports.project_factory import ProjectFactory


def create_project(self, project):
    project_id = project["name"]
    project["org_id"] = self.tf_ref("organization", "/")
    project["billing_account"] = self.created["vars"]["billing_id"].string_value
    project["name"] = project_id + \
        self.created["vars"]["project_suffix"].string_value

    if folder := project.get("folder_id"):
        if self.which_node(folder) == "folder":
            project["folder_id"] = self.tf_ref("folder", folder)
    if svpc_host := project.get("svpc_host_project_id"):
        project["svpc_host_project_id"] = self.tf_ref("project", svpc_host)
    if group_name := project.get("group_name"):
        group_id = f'{group_name}@{project.get("domain","")}'
        project["group_name"] = self.tf_ref("group_name", group_id, group_name)

    added_project = ProjectFactory(self, f"prj_{project_id}", **project)

    if shared_subnets := project.get("shared_vpc_subnets"):
        added_project.add_override(
            "shared_vpc_subnets",
            [
                self.tf_ref("subnet", region_subnet)
                for region_subnet in shared_subnets
            ],
        )
    self.created["projects"][project_id] = added_project


def generate_projects(self, my_resource, resource):
    for project in self.eztf_config.get(my_resource, []):
        if project.get("svpc_host_project_id"):
            continue
        create_project(self, project)
    generate_svc_projects(self, my_resource)


def generate_svc_projects(self, my_resource):
    add_svc_projects = [
        project
        for project in self.eztf_config.get(my_resource, [])
        if project.get("svpc_host_project_id")
    ]
    if add_svc_projects:
        self.file_seprator_variable("svcprojects", force=True)
    for project in add_svc_projects:
        create_project(self, project)
