
from imports.group import Group


def remove_group_member_overlap(group):
    group_owners = set(group.get("owners", []))
    group_managers = set(group.get("managers", []))
    group_members = set(group.get("members", []))
    group_managers = group_managers - group_owners
    group_members = group_members - group_managers - group_owners
    group["owners"] = list(group_owners)
    group["managers"] = list(group_managers)
    group["members"] = list(group_members)
    return group


def create_group(self, group):
    group_id = group["id"]
    self.created["groups"][group_id] = Group(
        self,
        f"grp_{group_id}",
        **group,
    )


def user_ref_group(self, group):
    for user_type in ["owners", "managers", "members"]:
        users = group[user_type]
        for i, user in enumerate(users):
            users[i] = self.tf_ref("user", user)


def generate_groups(self, my_resource, resource):
    for group in self.eztf_config.get(my_resource, []):
        group = remove_group_member_overlap(group)
        user_ref_group(self, group)
        create_group(self, group)
