from imports.google.storage_bucket import (
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
