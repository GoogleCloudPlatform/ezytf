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
