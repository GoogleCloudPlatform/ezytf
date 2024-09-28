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

from imports.pgsql import Pgsql
from imports.mssql import Mssql
from imports.mysql import Mysql


def create_cloudsql(self, sql, sql_type):
    sql_id = f"{sql_type}_{sql['name']}"

    sql["project_id"] = self.tf_ref("project", sql["project_id"])

    if sql.get("ip_configuration", {}).get("private_network"):
        sql["ip_configuration"]["private_network"] = self.tf_ref(
            "network", sql["ip_configuration"]["private_network"]
        )
    if sql.get("ip_configuration", {}).get("psc_allowed_consumer_projects", []):
        psc_consumer = []
        for project in sql["ip_configuration"]["psc_allowed_consumer_projects"]:
            psc_consumer.append(self.tf_ref("project", project))
        sql["ip_configuration"]["psc_allowed_consumer_projects"] = psc_consumer

    if sql_type == "pgsql":
        Pgsql(self, sql_id, **sql)
    elif sql_type == "mysql":
        Mysql(self, sql_id, **sql)
    elif sql_type == "mssql":
        Mssql(self, sql_id, **sql)


def generate_cloudsql(self, my_resource, resource):
    """creates sql"""
    for sql in self.eztf_config.get(my_resource, []):
        create_cloudsql(self, sql, resource)
