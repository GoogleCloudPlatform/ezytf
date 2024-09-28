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
