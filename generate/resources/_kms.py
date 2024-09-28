from imports.kms import Kms


def create_kms(self, kms):
    """creates sc access level"""
    name = kms["keyring"]
    kms["project_id"] = self.tf_ref("project", kms["project_id"])
    owners = []
    for owner in kms.get("owners", []):
        subowners = []
        for principal in owner.split(","):
            principal = principal.strip().split(":")
            p_type, principal_id = principal[0], principal[1]
            principal_id = self.tf_ref(p_type.lower(), principal_id)
            new_principal = f"{p_type}:{principal_id}"
            subowners.append(new_principal)
        subowners = ",".join(subowners)
        owners.append(subowners)
    if owners:
        kms["owners"] = owners
    self.created["kms"][name] = Kms(self, f"kms_{name}", **kms)


def generate_kms(self, my_resource, resource):
    """creates sc perimeter"""
    for data in self.eztf_config.get(my_resource, []):
        create_kms(self, data)
