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

from cdktf_cdktf_provider_google.storage_bucket import (
    StorageBucket,
    StorageBucketCors,
    StorageBucketLifecycleRule,
)


def create_gcs(self, gcs):
    """creates sc access level"""
    name = gcs["name"]
    gcs["project"] = self.tf_ref("project", gcs["project"])
    if gcs.get("cors"):
        gcs["cors"] = [StorageBucketCors(**cors) for cors in gcs["cors"]]
    if gcs.get("lifecycle_rule"):
        gcs["lifecycle_rule"] = [
            StorageBucketLifecycleRule(**lr) for lr in gcs["lifecycle_rule"]
        ]
    self.created["gcs"][name] = StorageBucket(self, f"gcs_{name}", **gcs)


def generate_gcs(self, my_resource, resource):
    """creates sc perimeter"""
    for data in self.eztf_config.get(my_resource, []):
        create_gcs(self, data)
