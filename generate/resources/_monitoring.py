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

from cdktf import (
    TerraformIterator,
    Token,
)
from cdktf_cdktf_provider_google.monitoring_monitored_project import (
    MonitoringMonitoredProject,
)
from cdktf_cdktf_provider_google.project_service import ProjectService


def create_monitoring_scope(self, mon):
    scoping, scoped = mon["scoping_project"], mon["monitored_project"]
    if scoping in scoped:
        scoped.remove(scoping)
    project_scoped = [self.tf_ref("project", scope) for scope in scoped]
    scoped_api = ProjectService(
        self,
        f"mon_api_{scoping}",
        service="monitoring.googleapis.com",
        project=self.tf_ref("project", scoping),
        disable_on_destroy=False,
        disable_dependent_services=False,
    )
    iterator = TerraformIterator.from_list(project_scoped)
    MonitoringMonitoredProject(
        self,
        f"ms_{scoping}",
        for_each=iterator,
        metrics_scope=scoped_api.project,
        name=Token.as_string(iterator.value),
    )


def generate_monitoring(self, my_resource, resource):
    for mon in self.eztf_config.get(my_resource, []):
        create_monitoring_scope(self, mon)
