# Copyright 2025 Google LLC
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


from cdktf_cdktf_provider_google.discovery_engine_data_store import (
    DiscoveryEngineDataStore,
    DiscoveryEngineDataStoreDocumentProcessingConfigParsingConfigOverrides,
)
from cdktf_cdktf_provider_google.discovery_engine_search_engine import (
    DiscoveryEngineSearchEngine,
)
from cdktf_cdktf_provider_google.discovery_engine_chat_engine import (
    DiscoveryEngineChatEngine,
)
from cdktf_cdktf_provider_google.discovery_engine_schema import DiscoveryEngineSchema
from cdktf_cdktf_provider_google.discovery_engine_target_site import (
    DiscoveryEngineTargetSite,
)


def create_datastore(self, datastore):
    """creates datastore"""
    name = datastore["data_store_id"]
    datastore["project"] = self.tf_ref("project", datastore["project"])

    if parsing_overrides := datastore.get("document_processing_config", {}).get(
        "parsing_config_overrides"
    ):
        datastore["document_processing_config"]["parsing_config_overrides"] = [
            DiscoveryEngineDataStoreDocumentProcessingConfigParsingConfigOverrides(**po)
            for po in parsing_overrides
        ]

    self.created["datastore"][name] = DiscoveryEngineDataStore(
        self, f"datastore_{name}", **datastore
    )


def generate_datastore(self, my_resource, resource):
    """creates datastore"""
    for data in self.eztf_config.get(my_resource, []):
        create_datastore(self, data)


def create_chat_engine(self, chat_engine):
    """creates chat engine"""
    name = chat_engine["engine_id"]
    chat_engine["project"] = self.tf_ref("project", chat_engine["project"])

    if cx := chat_engine.get("chat_engine_config", {}).get("dialogflow_agent_to_link"):
        chat_engine["chat_engine_config"]["dialogflow_agent_to_link"] = self.tf_ref(
            "cx", cx
        )

    if ds_list := chat_engine.get("data_store_ids"):
        chat_engine["data_store_ids"] = [self.tf_ref("datastore", ds) for ds in ds_list]

    self.created["chat_engine"][name] = DiscoveryEngineChatEngine(
        self, f"chat_engine_{name}", **chat_engine
    )


def generate_chat_engine(self, my_resource, resource):
    """creates chat engine"""
    for data in self.eztf_config.get(my_resource, []):
        create_chat_engine(self, data)


def create_search_engine(self, search_engine):
    """creates search engine"""
    name = search_engine["engine_id"]
    search_engine["project"] = self.tf_ref("project", search_engine["project"])

    if ds_list := search_engine.get("data_store_ids"):
        search_engine["data_store_ids"] = [
            self.tf_ref("datastore", ds) for ds in ds_list
        ]

    self.created["search_engine"][name] = DiscoveryEngineSearchEngine(
        self, f"search_engine_{name}", **search_engine
    )


def generate_search_engine(self, my_resource, resource):
    """creates search engine"""
    for data in self.eztf_config.get(my_resource, []):
        create_search_engine(self, data)


def create_de_schema(self, de_schema):
    """creates de schema"""
    name = de_schema["schema_id"]
    de_schema["project"] = self.tf_ref("project", de_schema["project"])

    de_schema["data_store_id"] = self.tf_ref("datastore", de_schema["data_store_id"])

    self.created["datastore_schema"][name] = DiscoveryEngineSchema(
        self, f"datastore_schema_{name}", **de_schema
    )


def generate_de_schema(self, my_resource, resource):
    """creates de schema"""
    for data in self.eztf_config.get(my_resource, []):
        create_de_schema(self, data)


def create_de_site(self, de_site):
    """creates de target site"""
    name = de_site["data_store_id"]
    de_site["project"] = self.tf_ref("project", de_site["project"])

    de_site["data_store_id"] = self.tf_ref("datastore", de_site["data_store_id"])

    self.created["datastore_targetsite"][name] = DiscoveryEngineTargetSite(
        self, f"datastore_targetsite_{name}", **de_site
    )


def generate_de_site(self, my_resource, resource):
    """creates de target site"""
    for data in self.eztf_config.get(my_resource, []):
        create_de_site(self, data)

