import hashlib
from cdktf import TerraformLocal, Fn
from imports.google.data_google_service_account_access_token import (
    DataGoogleServiceAccountAccessToken,
)
from imports.googleworkspace.provider import GoogleworkspaceProvider
from imports.googleworkspace.user import User
import util


def init_workspace_provider(self, users):
    setup_sa = self.created["vars"]["setup_service_account"].string_value
    sa_token_access = DataGoogleServiceAccountAccessToken(
        self,
        "sa",
        target_service_account=setup_sa,
        scopes=[
            "userinfo-email",
            "cloud-platform",
            "https://www.googleapis.com/auth/admin.directory.user",
        ],
    )
    user_pass = {
        user["primary_email"]: hashlib.md5(util.random_str().encode()).hexdigest()
        for user in users
    }
    self.created["locals"]["users_hash_pass"] = TerraformLocal(
        self, "users_hash_password", user_pass
    )
    self.created["locals"]["change_password_at_next_login"] = TerraformLocal(
        self, "change_password_at_next_login", True
    )

    GoogleworkspaceProvider(
        self,
        id="googleworkspace",
        customer_id=self.created["data"]["google_org"].directory_customer_id,
        access_token=sa_token_access.access_token,
    )


def create_user(self, user):
    user_id = user["primary_email"]
    user["password"] = Fn.lookup(
        self.created["locals"]["users_hash_pass"].as_string_map, user_id
    )
    user["hash_function"] = "MD5"
    user["change_password_at_next_login"] = self.created["locals"][
        "change_password_at_next_login"
    ].as_boolean
    self.created["users"][user_id] = User(
        self,
        f"user_{user_id}",
        **user,
    )


def generate_users(self, my_resource, resource):
    self.ensure_data(["google_org"])
    add_users = self.eztf_config.get(my_resource)
    if add_users:
        init_workspace_provider(self, add_users)
        for user in add_users:
            create_user(self, user)
