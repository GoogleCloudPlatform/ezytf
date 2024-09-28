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

from imports.log_export import LogExport
from imports.logbucket import Logbucket
from imports.logpubsub import Logpubsub
from imports.logstorage import Logstorage
from imports.logproject import Logproject
from imports.logbigquery import Logbigquery


log_destination_fn = {
    "pubsub": Logpubsub,
    "storage": Logstorage,
    "logbucket": Logbucket,
    "bigquery": Logbigquery,
    "project": Logproject,
    "logpubsub": Logpubsub,
    "logstorage": Logstorage,
    "logbigquery": Logbigquery,
    "logproject": Logproject,
}


def create_centralized_logging(self, logconfig):
    """creates centralized logging"""
    logsink = logconfig["logsink"]
    log_destination_type = (set(logconfig.keys()) - {"logsink"}).pop()
    log_destination = logconfig[log_destination_type]

    logsink["parent_resource_id"] = self.tf_ref(
        logsink["parent_resource_type"],
        logsink.get("parent_resource_id", ""),
    )
    # log_sink_writer_identity not actually used, added because required field
    log_destination["log_sink_writer_identity"] = (
        "serviceAccount:cloud-logs@system.gserviceaccount.com"
    )
    sink_name = logsink["log_sink_name"]
    sink_id = f"logsink-{sink_name}"
    log_destination["project_id"] = self.tf_ref(
        "project", log_destination["project_id"]
    )

    created_log_destination = log_destination_fn[log_destination_type](
        self,
        f"{log_destination_type}-{sink_name}",
        **log_destination,
    )
    created_log_destination.add_override(
        "log_sink_writer_identity", f"${{module.{sink_id}.writer_identity}}"
    )

    LogExport(
        self,
        sink_id,
        destination_uri=created_log_destination.destination_uri_output,
        **logsink,
    )


def generate_logging(self, my_resource, resource):
    for lx in self.eztf_config.get(my_resource, []):
        create_centralized_logging(self, lx)


log_destination_name_map = {
    "logpubsub": "topic_name",
    "logstorage": "storage_bucket_name",
    "logbucket": "name",
    "logbigquery": "dataset_name",
    "logproject": "project_id",
}


def create_log_destination(self, log_destination, log_dest_type):
    writer_identity = log_destination.get("log_sink_writer_identity", "")
    name_key = log_destination_name_map.get(log_dest_type)
    dest_name = log_destination[name_key]
    dest_id = f"{log_dest_type}-{dest_name}"
    sink_name = self.added.get("log_destination", {}).get(dest_id)
    sink_id = f"logsink-{sink_name}" if sink_name else None

    log_destination["project_id"] = self.tf_ref(
        "project", log_destination["project_id"]
    )
    if not writer_identity:
        # backup log_sink_writer_identity required field
        log_destination["log_sink_writer_identity"] = (
            "serviceAccount:cloud-logs@system.gserviceaccount.com"
        )

    self.created["log_destination"][dest_id] = log_destination_fn[log_dest_type](
        self,
        dest_id,
        **log_destination,
    )

    if not writer_identity and sink_id:
        self.created["log_destination"][dest_id].add_override(
            "log_sink_writer_identity", f"${{module.{sink_id}.writer_identity}}"
        )


def create_logsink(self, logsink):
    log_dest_type = logsink["log_destination_type"]
    sink_name = logsink["log_sink_name"]
    dest_uri = logsink["destination_uri"]
    sink_id = f"logsink-{sink_name}"
    dest_id = f"{log_dest_type}-{dest_uri}"
    del logsink["log_destination_type"]
    if log_dest_type == "logproject":
        create_log_destination(self, {"project_id": dest_uri}, "logproject")

    logsink["parent_resource_id"] = self.tf_ref(
        logsink["parent_resource_type"],
        logsink.get("parent_resource_id", ""),
    )
    logsink["destination_uri"] = self.tf_ref("log_destination", dest_id, dest_uri)

    LogExport(
        self,
        sink_id,
        **logsink,
    )


def generate_logsink(self, my_resource, resource):
    self.created["log_destination"] = self.created.get("log_destination", {})
    for sink in self.eztf_config.get(my_resource, []):
        create_logsink(self, sink)


def generate_log_destination(self, my_resource, resource):
    self.created["log_destination"] = self.created.get("log_destination", {})
    for log_dest in self.eztf_config.get(my_resource, []):
        create_log_destination(self, log_dest, resource)


def add_dest_sink_map(self, my_resource, resource):
    self.added["log_destination"] = self.added.get("log_destination", {})
    for logsink in self.eztf_config.get(my_resource, []):
        log_dest_type = logsink["log_destination_type"]
        sink_name = logsink["log_sink_name"]
        dest_uri = logsink["destination_uri"]
        dest_id = f"{log_dest_type}-{dest_uri}"
        self.added["log_destination"][dest_id] = sink_name
