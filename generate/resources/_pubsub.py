from imports.ff_pubsub import FfPubsub


def create_ff_pubsub(self, pubsub):
    name = pubsub["name"]
    pubsub["project_id"] = self.tf_ref("project", pubsub["project_id"])

    self.update_fabric_iam(pubsub)

    for _, sub in pubsub.get("subscriptions", {}).items():
        self.update_fabric_iam(sub)

    FfPubsub(
        self,
        name,
        **pubsub,
    )


def generate_ff_pubsub(self, my_resource, resource):
    for pubsub in self.eztf_config.get(my_resource, []):
        create_ff_pubsub(self, pubsub)
