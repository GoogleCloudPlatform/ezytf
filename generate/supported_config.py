import json
import requests
import time

SLEEP_SECONDS = 1

def supported_tf_json():
    from resources import creation
    with open("supported_tf.json", "w", encoding="utf-8") as fp:
        json.dump(list(creation.keys()), fp, indent=2, sort_keys=True)



def get_latest_github_release(owner_repo):
    url = f"https://api.github.com/repos/{owner_repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    release =  response.json()
    print(release)
    return release.get('tag_name')


def git_repo_release(repos_dic):
    result = {}
    for source, owner_repo in repos_dic.items():
        time.sleep(SLEEP_SECONDS)
        latest_tag = get_latest_github_release(owner_repo)
        print(f"--- Latest Release for {owner_repo} --- {latest_tag}")
        result[source] = latest_tag
    return result


def module_owner_repo(source):
    repo_sp = source.split('/')
    owner, repo_name = repo_sp[0], f"terraform-{repo_sp[2]}-{repo_sp[1]}"
    mod_source = '/'.join(repo_sp[:3])
    return f"{owner}/{repo_name}", mod_source

def cdktf_json_repo():
    with open("cdktf.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)
    tf_modules = data.get("terraformModules")

    source_owner_repo = {}
    mod_source_map = {}
    for item in tf_modules:
        source = item.get("source")
        if not source.startswith("git::"):
            owner_repo, mod_source = module_owner_repo(source)
            if not source_owner_repo.get(mod_source):
                source_owner_repo[mod_source] = owner_repo
            mod_source_map[source] = mod_source

    ver_result = git_repo_release(source_owner_repo)

    for item in data.get("terraformModules",[]):
        source = item.get("source")
        mod_source = mod_source_map.get(source)
        if item.get("version") and source and mod_source and ver_result.get(mod_source):
            version = ver_result[mod_source].lstrip('v')
            item["version"] = f"~> {version}"            
            
    print(ver_result)

    with open("cdktf.json", "w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)


if __name__ == "__main__":
    supported_tf_json()
    cdktf_json_repo()

