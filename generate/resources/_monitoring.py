from cdktf import (
    TerraformIterator,
    Token,
)
from imports.google.monitoring_monitored_project import MonitoringMonitoredProject
from imports.google.project_service import ProjectService


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
