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

from imports.google.service_account import ServiceAccount


def create_sa(self, sa):
    "create service account"
    tf_sa_id = f'sa_{sa["account_id"]}_{sa["project"]}'
    name = f'{sa["account_id"]}@{sa["project"]}.iam.gserviceaccount.com'
    sa["project"] = self.tf_ref("project", sa["project"])

    self.created["service_account"][name] = ServiceAccount(self, tf_sa_id, **sa)


def generate_sa(self, my_resource, resource):
    "create service account"
    for sa in self.eztf_config.get(my_resource, []):
        create_sa(self, sa)
