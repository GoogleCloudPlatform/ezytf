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

import hashlib
from cdktf import TerraformLocal, Fn
from cdktf_cdktf_provider_google.data_google_service_account_access_token import (
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
        customer_id=self.tf_ref("customer_id", ""),
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
