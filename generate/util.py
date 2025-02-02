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

import random
import string
import os
import re
from datetime import datetime
import yaml
import json
import google.auth
import google.auth.credentials
import google.oauth2.credentials
import google.auth.transport.requests
from google.cloud import storage
from git import Repo
import requests

RANDOM_WORD = "gcp-cdk-tf-id_"
TF_SINGLE_OUT = "cdktf.out/stacks/{stack_name}/cdk.tf"

continent_short_name = {
    "africa": "af",
    "asia": "az",
    "australia": "au",
    "europe": "eu",
    "northamerica": "na",
    "southamerica": "sa",
    "us": "us",
    "me": "me",
}
DIR_REGEX = r"(n)orth|(s)outh|(e)ast|(w)est|(c)entral"
DIR_SUBS = "\\1\\2\\3\\4\\5"


def cdktf_output(stack_name, output_folder="cdktf.out"):
    return f"{output_folder}/stacks/{stack_name}/cdk.tf"


def clean_principal_id(name: str) -> str:
    """returns clean principal id"""
    if name.startswith("principalSet:") or name.startswith("principal:"):
        return name.split("/")[-1]
    return name.replace(":", "_").replace(".", "").replace("@", "")


def clean_res_id(name):
    """returns resource id name lowercase and hypen"""
    return name.lower().replace(".", "-").replace("_", "-")


def lower(name):
    """return lower case name replaces with underscore"""
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    return name


def clean_tf_folder(name):
    """returns clean folder td id string"""
    name = str(name)
    if not name:
        return "org"
    if name[0] == "/":
        name = name[1:]
    return name.replace("/", "__")


def time_str():
    "return human readable time"
    return datetime.now().strftime("%Y-%m-%d_%H-%M")


def random_str(n=8):
    """returns random string, N is length of string, default - 8"""
    return "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=n
        )
    )


def short_region(region):
    """return short region or zone name"""
    cot_reg = region.split("-")
    cot_reg[0] = continent_short_name[cot_reg[0]]
    cot_reg[1] = re.sub(DIR_REGEX, DIR_SUBS, cot_reg[1])
    return "".join(cot_reg)


def pascal_case(name: str):
    return name.replace("_", " ").title().replace(" ", "")


def get_file_yaml(filename):
    "returns yaml as dict"
    with open(filename, "r", encoding="utf-8") as fp:
        yaml_dict = yaml.safe_load(fp)
    return yaml_dict


def write_file_yaml(filename, dict_data):
    "creates yaml file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fp:
        yaml.safe_dump(dict_data, fp, sort_keys=False, default_flow_style=False)


def write_file_json(filename, dict_data):
    "creates json file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(dict_data, fp, indent=4, sort_keys=False)


def write_file_any(filename, content):
    "creates json file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fp:
        fp.write(content)


def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


def download_from_gcs(bucket_name, source_blob_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    os.makedirs(os.path.dirname(source_blob_name), exist_ok=True)
    blob.download_to_filename(source_blob_name)
    print(f"Blob {source_blob_name} downloaded to {source_blob_name}.")
    contents = blob.download_as_string().decode("utf-8")
    return contents


def upload_folder_to_gcs(bucket_name, local_folder, gcs_prefix=""):
    """Uploads a folder to the bucket recursively."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for path, dirs, files in os.walk(local_folder):
        # skip hidden files
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        files = [f for f in files if not f.startswith(".")]
        for name in files:
            local_file = os.path.join(path, name)
            local_file_path = os.path.relpath(local_file, local_folder)
            blob_name = os.path.join(gcs_prefix, local_file_path)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_file)
        print(f"Files {','.join(files)} uploaded to gs://{bucket_name}/{gcs_prefix}")


def tf_vars_file(variables, output_folder):
    """
    Creates a tfvars file from a dictionary of variables.

    Args:
        variables: A dictionary of variables, where the key is the variable name
            and the value is the variable value.
        output_folder: The path to the folder where the tfvars file should be saved.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, "terraform.tfvars")
    with open(output_file, "w", encoding="utf-8") as f:
        for key, value in variables.items():
            if isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f"{key} = {value}\n")


def split_tf_file(input_file, output_folder):
    """Splits a .tf file into multiple files based on the variable pattern.

    Args:
        input_file: Path to the input .tf file.
        output_folder: Path to the folder where output files will be saved.
    """

    os.makedirs(output_folder, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    tf_content = re.sub(r"\"\$\{(.+)\}\"", "\\1", content)

    pattern = rf"variable\s+\"{RANDOM_WORD}(file_.*?)\"\s+\{{\s*\}}"
    tf_list = re.split(pattern, tf_content)

    filename = "backend"
    i = 0
    j = 0
    output_files = []
    while i < len(tf_list):
        tfdata = tf_list[i]
        i += 1
        if match := re.search(r"^file_(\S+)$", tfdata):
            filename = match.group(1)
            continue
        j += 1
        filename = filename or f"file_{j}"
        filename = f"{filename}.tf"
        output_file = os.path.join(output_folder, filename)
        output_files.append(filename)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(tfdata)
        filename = ""
    print(f"Created files: {','.join(output_files)} in {output_folder}")


def ssm_url_extract(url):
    """Extract instance_id, project_number & location
    {instance_id}-{project_number}-api.{location}.sourcemanager.dev"""
    ssm_host = url.replace("https://", "").replace("http://", "")
    ssm_li = ssm_host.split(".")
    location = ssm_li[1]
    ssm_sub = ssm_li[0].removesuffix("-api").split("-")
    instance_id, project_number = "-".join(ssm_sub[:-1]), ssm_sub[-1]
    return instance_id, project_number, location


def ssm_repository(repo_name, ssm_url):
    """Lists repositories in a Secure Source Manager instance using the requests library."""

    instance_id, project_number, location = ssm_url_extract(ssm_url)
    access_token = get_access_token()
    repo_uri = f"projects/{project_number}/locations/{location}/repositories"
    base_url = (
        f"https://{instance_id}-{project_number}-api.{location}.sourcemanager.dev/v1/"
    )
    repo_id = f"{repo_uri}/{repo_name}"
    url = f"{base_url}/{repo_uri}"
    headers = {"Authorization": f"Bearer {access_token}"}

    # list repositories
    params = {}
    next_page = None
    while True:
        if next_page:
            params = {"page_token": next_page}
        response = requests.get(url, params=params, headers=headers, timeout=120)
        rep = response.json()
        if not response.ok:
            print("list repositories failed", rep)
            response.raise_for_status()
        rep = response.json()
        for repo in rep.get("repositories", []):
            if repo.get("name") == repo_id:
                print(f"git repo present, skipping creation {repo['uris']['gitHttps']}")
                return repo["uris"]["gitHttps"]
        next_page = rep.get("nextPageToken")
        if not next_page:
            break

    # create repository
    response = requests.post(
        url, headers=headers, params={"repository_id": repo_name}, data={}, timeout=120
    )
    rep = response.json()
    if not response.ok:
        print("create repository failed", rep)
        response.raise_for_status()
    created_repo = ""
    try:
        created_repo = rep["response"]["uris"]["gitHttps"]
    except KeyError:
        print("create repository failed", rep)
    print(f"ssm git repo created{created_repo}")
    return created_repo


def push_folder_to_git(repo_path, remote_url, branch_name="main"):
    """Pushes the contents of an existing folder to a Git repository.

    Args:
        repo_path: Local path to the folder (already initialized as a Git repository).
        remote_url: The URL of the remote git repository (e.g., "https://github.com/your-username/your-repo.git").
        branch_name: The branch to push to (defaults to "main").
    """

    repo = Repo.init(repo_path)

    if branch_name not in repo.heads:
        repo.git.checkout("-b", branch_name)
    else:
        repo.heads[branch_name].checkout()

    # Add, commit, and push changes
    repo.git.add(all=True, force=True)
    repo.index.commit("eztf auto commit")

    # Add remote
    if "origin" not in repo.remotes:
        repo.create_remote("origin", remote_url)

    origin = repo.remotes.origin
    r = re.compile(r"refs/tags/0\.(\d+)-auto")
    max_tag = 0
    # below command returns
    # 0206504b3460ac4e63e28461c525a3708f20a960        refs/tags/0.1-auto
    rem_tag = repo.git.ls_remote("--tags", "origin", "0.*-auto").strip()

    for tagline in rem_tag.split("\n"):
        tagl = tagline.strip().split()
        if len(tagl) < 2:
            continue
        if match := r.match(tagl[1].strip()):
            curr_tag = int(match.group(1))
            max_tag = max(curr_tag, max_tag)
    max_tag += 1
    tag = f"0.{max_tag}-auto"
    repo.create_tag(tag)
    print(f"pushing branch {branch_name} & tag {tag} to {remote_url}")
    origin.push(
        refspec=[f"{branch_name}:{branch_name}", f"{tag}:{tag}"],
        force=True,
        atomic=True,
    )
    print("Successfully pushed to Remote Git")


def get_env_token():
    return os.environ.get("EZTF_GCLOUD_ACCESS")


def get_access_token():
    auth_req = google.auth.transport.requests.Request()
    gcp_token = google.oauth2.credentials.UserAccessTokenCredentials()
    gcp_token.refresh(request=auth_req)
    return gcp_token.token
