import os
import util

REPO_TEMPLATE_FILE = {
    "_setup_script": [
        ("setup_project.sh", "../templates/tf_repo/setup_project.sh"),
        ("README.md", "../templates/tf_repo/setup_project_README.md"),
    ],
    "_root": [("README.md", "../templates/root_repo/order_README.md")],
    "tf": [
        ("README.md", "../templates/tf_repo/tf_README.md"),
    ],
    "users": [("README.md", "../templates/tf_repo/users_README.md")],
    "groups": [("README.md", "../templates/tf_repo/groups_README.md")],
}


SETUP_VAR_ENV = [
    "organization_id",
    "setup_project_id",
    "setup_iam_resource",
    "setup_iam_resource_id",
    "setup_service_account_name",
    "setup_service_account",
    "setup_gcs",
    "setup_gcs_location",
    "GOOGLE_IMPERSONATE_SERVICE_ACCOUNT",
    "USER_PROJECT_OVERRIDE",
    "GOOGLE_BILLING_PROJECT",
    "GOOGLE_PROJECT",
    "setup_apis",
    "setup_roles",
]

def create_templated_file(repo_folder, template_list, vars):
    uniq_dest_file = set()
    for templ_key in template_list:
        for dest_file_name, template_file in REPO_TEMPLATE_FILE.get(templ_key, []):
            uniq_dest_file.add(dest_file_name)
            dest_file = os.path.join(repo_folder, os.path.basename(dest_file_name))
            util.write_or_append_file(template_file, dest_file, vars)
    if uniq_dest_file:
        print(
            f"Created files: {','.join(uniq_dest_file)} in {'/'.join(repo_folder.split('/')[-2:])}"
        )


def setup_script(repo_folder, vars, is_tf):
    "add scripts file and env var in repo folder"
    script_var = {}

    for var in set(SETUP_VAR_ENV).intersection(vars):
        script_var[var] = vars[var]

    script_var["setup_project_id"] = script_var.get("setup_project_id", "$project_id")
    project_id = script_var["setup_project_id"]

    if not script_var.get("setup_service_account"):
        if sa_name := script_var.get("setup_service_account_name"):
            script_var["setup_service_account"] = (
                f"{sa_name}@{project_id}.iam.gserviceaccount.com"
            )

    if is_tf:
        if sa := script_var.get("setup_service_account"):
            script_var["GOOGLE_IMPERSONATE_SERVICE_ACCOUNT"] = sa
        if script_var.get("setup_project_id"):
            script_var["USER_PROJECT_OVERRIDE"] = "true"
            script_var["GOOGLE_BILLING_PROJECT"] = project_id
            script_var["GOOGLE_PROJECT"] = project_id

    script_var["setup_apis"] = util.str_list(script_var.get("setup_apis", []))
    script_var["setup_roles"] = util.str_list(script_var.get("setup_roles", []))

    env_li = []
    for name in SETUP_VAR_ENV:
        if script_var.get(name) is not None:
            env_li.append((name, script_var[name]))
    env_str = util.python_to_bash_vars(env_li, export=True)

    util.write_file_any(f"{repo_folder}/script_env", env_str)
    create_templated_file(repo_folder, ["_setup_script"], script_var)
