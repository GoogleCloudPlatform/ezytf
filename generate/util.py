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
import shlex
import shutil
import urllib.parse
import google.auth
import google.auth.credentials
import google.oauth2.credentials
import google.auth.transport.requests
from google.cloud import storage
from google.cloud.storage import transfer_manager
from git import Repo
import requests
import jinja2

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

jinja_env = jinja2.Environment()


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

_find_unsafe = re.compile(r'[^\w@$%+=:,./-]', re.ASCII).search

def shell_quote(s):
    """Return a shell-escaped version of the string *s*."""
    if isinstance(s, bool):
        return "true" if s else "false"
    s = str(s)
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s
    return "'" + s.replace("'", "'\"'\"'") + "'"

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


def camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def str_list(item, sep=","):
    if isinstance(item, list):
        return sep.join(item)
    elif isinstance(item, str):
        return sep.join([i.strip() for i in item.split(sep) if i.strip()])
    return item


def dict_without_prefixes(data_dict, prefix_li, skip_keys=[]):
    new_dict = {}
    for key, value in data_dict.items():
        if key in skip_keys:
            continue
        skip_prefix = False
        for prefix in prefix_li:
            if key.startswith(prefix):
                skip_prefix = True
                break
        if not skip_prefix:
            new_dict[key] = value
    return new_dict


def nested_list_keys_to_camel(data):
    def process_item(item, in_list=False):
        if isinstance(item, dict):
            new_item = {}
            for key, value in item.items():
                if in_list:
                    new_key = camel_case(key)
                else:
                    new_key = key
                new_item[new_key] = process_item(value, in_list)
            return new_item
        elif isinstance(item, list):
            return [process_item(v, True) for v in item]
        else:
            return item

    if not isinstance(data, dict):
        return data

    result = process_item(data)
    return result


def eztf_filename(name, extension, default, count=0):
    filename = name
    if not name:
        file_suffix = "" if count == 0 else "_" + str(count)
        filename = default + file_suffix
    if extension and not filename.endswith(f".{extension}"):
        filename += f".{extension}"
    return filename


def get_file_yaml(filename):
    "returns yaml as dict"
    with open(filename, "r", encoding="utf-8") as fp:
        yaml_dict = yaml.safe_load(fp)
    return yaml_dict


def write_file_yaml(filename, data):
    "creates yaml file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fp:
        yaml.safe_dump(data, fp, sort_keys=False, default_flow_style=False)


def write_file_json(filename, data):
    "creates json file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=4, sort_keys=False)


def write_file_jsonl(filename, data):
    "creates jsonl file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fp:
        for item in data:
            json.dump(item, fp)
            fp.write("\n")


def write_file_any(filename, content, jinja_vars=None, mode="w"):
    "creates any file"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if jinja_vars and len(jinja_vars) > 0:
        template = jinja_env.from_string(content)
        content = template.render(jinja_vars)
    with open(filename, mode, encoding="utf-8") as fp:
        fp.write(content)


def write_or_append_file(
    source_file, destination_file, jinja_vars=None, force_write=False
):
    with open(source_file, "r", encoding="utf-8") as fp:
        content = fp.read()
    mode = "w"
    if os.path.exists(destination_file) and not force_write:
        mode = "a"
        content = "\n\n" + content
    write_file_any(destination_file, content, jinja_vars, mode)


def delete_folders(folder_li):
    for folder in folder_li:
        shutil.rmtree(folder, ignore_errors=True)


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


def folder_files(local_folder):
    result = []
    for path, dirs, files in os.walk(local_folder):
        # skip hidden files
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        files = [f for f in files if not f.startswith(".")]
        for name in files:
            local_file = os.path.join(path, name)
            folder_file_path = os.path.relpath(local_file, local_folder)
            result.append((local_file, folder_file_path))
    return result


def upload_folder_to_gcs(bucket_name, local_folder, gcs_prefix=""):
    """Uploads a folder to the bucket recursively."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for local_file, folder_file_path in folder_files(local_folder):
        blob_name = os.path.join(gcs_prefix, folder_file_path)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_file)


def upload_folder_to_gcs_parallel(bucket_name, local_folder, gcs_prefix=""):
    """Uploads a folder to the bucket parallely."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    gcs_prefix = gcs_prefix.rstrip("/") + "/" if gcs_prefix else ""
    filenames = [folder_file_path for _, folder_file_path in folder_files(local_folder)]

    results = transfer_manager.upload_many_from_filenames(
        bucket,
        filenames,
        source_directory=local_folder,
        blob_name_prefix=gcs_prefix,
    )
    for name, result in zip(filenames, results):
        if isinstance(result, Exception):
            print("Failed to upload {name} due to exception: {result}")
    print(
        f"uploaded files in {local_folder.split('/')[-1]} to gs://{bucket_name}/{gcs_prefix}"
    )


def _to_hcl_value(value, indent_level=0, indent_spaces=2):
    """
    Converts a Python value to its HCL string representation for .tfvars.
    """
    current_indent = " " * (indent_level * indent_spaces)
    next_indent = " " * ((indent_level + 1) * indent_spaces)

    if isinstance(value, str):
        escaped_value = json.dumps(value)[1:-1]
        return f'"{escaped_value}"'
    elif isinstance(value, (int, float, bool)):
        return str(value).lower()
    elif value is None:
        return "null"
    elif isinstance(value, (list, tuple)):
        if not value:
            return "[]"
        items_hcl = [
            f"{next_indent}{_to_hcl_value(item, indent_level + 1, indent_spaces)}"
            for item in value
        ]
        return f"[\n{',\n'.join(items_hcl)},\n{current_indent}]"
    elif isinstance(value, dict):
        if not value:
            return "{}"
        pairs_hcl = []
        for k, v_item in value.items():
            key_hcl = f'"{k}"' if "-" in str(k) else str(k)
            val_hcl = _to_hcl_value(v_item, indent_level + 1, indent_spaces)
            pairs_hcl.append(f"{next_indent}{key_hcl} = {val_hcl}")
        return f"{{\n{'\n'.join(pairs_hcl)}\n{current_indent}}}"
    else:
        escaped_fallback = json.dumps(json.dumps(value)[1:-1])
        print(
            f"Warning: Unsupported type {type(value)} for HCL conversion. Representing as an escaped string: {value}"
        )
        return escaped_fallback


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
    tfvars_lines = []
    for key, value in variables.items():
        hcl_value_str = _to_hcl_value(value, indent_level=0, indent_spaces=2)
        tfvars_lines.append(f"{key} = {hcl_value_str}")

    tfvars_content = "\n\n".join(tfvars_lines) + "\n"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(tfvars_content)


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
    print(
        f"Created files: {','.join(output_files)} in {'/'.join(output_folder.split('/')[-2:])}"
    )


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
                # print(f"git repo present, skipping creation {repo['uris']['gitHttps']}")
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
    print(f"ssm git repo created {created_repo}")
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
    origin.push(
        refspec=[f"{branch_name}:{branch_name}", f"{tag}:{tag}"],
        force=True,
        atomic=True,
    )
    print(f"Successfully pushed branch {branch_name} & tag {tag} to {remote_url}")


def quote_shell_variable(str):
    return re.sub(r"(\$\{[^}]+\}|\$\([^)]+\))", r"'\1'", str)


def bash_str(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def python_to_bash_vars(vars, export=False):
    """
    Generates Bash variable declaration code from a dict / key,val tuple of list of Python variables.
    Args:
        vars (dict/list): A dictionary where keys are the desired Bash variable
                          names (str) and values are the Python variables
                          (str, int, bool, list, or dict).

    Returns:
        str: The generated Bash code as a single string.
    """
    bash_commands = []
    export_str = "export " if export else ""
    var_list = []
    if isinstance(vars, dict):
        var_list = list(vars.items())
    elif isinstance(vars, list):
        var_list = vars

    for name, value in var_list:
        if not name or not name.isidentifier() or name[0].isdigit():
            print(f"Invalid variable: '{name}'. Must start with letter or underscore")
            continue

        if isinstance(value, (str, int, bool, float)):
            bash_commands.append(f"{export_str}{name}={shell_quote(value)}")

        elif isinstance(value, list):
            val = ""
            if export:
                val = ",".join(value)
            else:
                # Indexed array assignment: my_array=( "item 1" "item 2" ... )
                val = f"( {' '.join([shell_quote(item) for item in value])} )"
            bash_commands.append(f"{export_str}{name}={val}")

        elif isinstance(value, dict):
            # Associative array assignment (Bash 4.0+): declare -A my_assoc=( [key1]="val1" [key2]="val2" ... )
            # Note: Both keys and values are converted to strings and quoted.
            items_str = []
            for k, v in value.items():
                items_str.append(
                    f"[{shlex.quote(bash_str(k))}]={shell_quote(v)}"
                )
            bash_commands.append(f"declare -A {name}=({' '.join(items_str)})")
        else:
            print(f"Unsupported '{name}': {type(value)}. Only str, list, dict are supported")

    output_string = "\n".join(bash_commands)
    return output_string


def generate_command(cmd, options, vars):
    command = cmd
    vars_cmd = ""
    if vars:
        vars_cmd = python_to_bash_vars(vars) + "\n\n"
    for key, value in options.items():
        option_val = f"={value}" if value else ""
        command.append(f"--{key}{option_val}")
    command_str = " ".join(command)
    return vars_cmd + command_str


def generate_curl_command(
    url="",
    method="GET",
    params=None,
    headers=None,
    data=None,
    json_data=None,
    options=None,
    vars=None,
    **kwargs,
):
    """
    Generates a cURL command string with proper shell quoting.

    Args:
        url (str): The target URL.
        method (str, optional): HTTP method (GET, POST, PUT, DELETE, etc.).
                                Defaults to 'GET'.
        headers (dict, optional): Dictionary of request headers
                                  (e.g., {'Content-Type': 'application/json'}).
                                  Defaults to None.
        params (dict, optional): Dictionary of query parameters to be appended
                                 to the URL (e.g., {'search': 'query', 'page': 2}).
                                 Keys and values will be URL-encoded.
                                 Defaults to None.
        data (str, optional): Request body data as a raw string. Used with '-d'.
                              Defaults to None.
        json_data (dict, optional): Request body data as a Python dictionary.
                                    Will be automatically JSON serialized.
                                    Sets 'Content-Type: application/json' header
                                    if not already present. Takes precedence over 'data'.
                                    Defaults to None.
        options (list, optional): List of additional raw cURL options/flags
                                   (e.g., ['-v', '-L', '-k', '--http1.1']).
                                   Defaults to None.

    Returns:
        str: The generated cURL command string.
    """
    if not json_data:
        json_data = kwargs.get("json")

    command_parts = []
    vars_cmd = ""
    if vars:
        vars_cmd = python_to_bash_vars(vars) + "\n\n"

    initial_parts = ["curl"]

    # Use this to pass flags like -v, -L, -k, -i, -o, -A etc.
    if options:
        initial_parts.append(" ".join(options))

    processed_method = method.upper()
    initial_parts.append("-X " + processed_method)

    command_parts.append(" ".join(initial_parts))

    final_headers = headers.copy() if headers else {}

    if json_data is not None and "Content-Type" not in final_headers:
        final_headers["Content-Type"] = "application/json"

    if final_headers:
        for key, value in final_headers.items():
            header_str = f"{key}: {value}"
            command_parts.append("-H " + f'"{header_str}"')

    final_url = url
    if params:
        query_string = urllib.parse.urlencode(params, doseq=True)
        final_url = f"{url}?{query_string}"

    command_parts.append(f'"{final_url}"')

    # --- Data Payload ---
    payload = None
    if json_data is not None:
        payload = json.dumps(json_data, indent=2)
        payload = quote_shell_variable(payload)
    elif data is not None:
        payload = data

    if payload is not None:
        command_parts.append(f"-d '{payload}'")

    return vars_cmd + " \\ \n".join(command_parts)


def get_env_token():
    return os.environ.get("EZTF_GCLOUD_ACCESS")


def get_access_token():
    auth_req = google.auth.transport.requests.Request()
    gcp_token = google.oauth2.credentials.UserAccessTokenCredentials()
    gcp_token.refresh(request=auth_req)
    return gcp_token.token
