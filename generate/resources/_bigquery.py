from imports.google.bigquery_dataset import (
    BigqueryDataset,
    BigqueryDatasetAccess,
)
from imports.google.bigquery_table import (
    BigqueryTable,
    BigqueryTableTableConstraintsForeignKeys,
    BigqueryTableExternalDataConfigurationBigtableOptionsColumnFamily,
    BigqueryTableExternalDataConfigurationBigtableOptionsColumnFamilyColumn,
)
from imports.google.bigquery_routine import (
    BigqueryRoutine,
    BigqueryRoutineArguments,
)


def create_bq_dataset(self, dataset):
    "create dataset"
    dataset_name = dataset["dataset_id"]
    dataset["project"] = self.tf_ref("project", dataset["project"])

    for access in dataset.get("access", []):
        if access.get("dataset_id"):
            access["dataset_id"] = self.tf_ref("bq_dataset", access["dataset_id"])
        if access.get("project_id"):
            access["project_id"] = self.tf_ref("bq_project", access["project_id"])
        if access.get("routine_id"):
            access["routine_id"] = self.tf_ref("bq_routine", access["routine_id"])
    self.tf_param_list(dataset, "access", BigqueryDatasetAccess)

    self.created["bq_dataset"][dataset_name] = BigqueryDataset(
        self, f"bqd_{dataset_name}", **dataset
    )


def create_bq_table(self, bqt):
    "create bqt"
    bqt_name = bqt["table_id"]
    bqt["dataset_id"] = self.tf_ref("dataset_id", bqt["dataset_id"])
    bqt["project"] = self.tf_ref("project", bqt["project"])

    if bqt.get("table_constraints", {}):
        self.tf_param_list(
            bqt["table_constraints"],
            "foreign_keys",
            BigqueryTableTableConstraintsForeignKeys,
        )
    bigtable_option = bqt.get("external_data_configuration", {}).get(
        "bigtable_options", {}
    )
    for btcf in bigtable_option.get("column_family", []):
        self.tf_param_list(
            btcf,
            "column",
            BigqueryTableExternalDataConfigurationBigtableOptionsColumnFamilyColumn,
        )
    self.tf_param_list(
        bigtable_option,
        "column_family",
        BigqueryTableExternalDataConfigurationBigtableOptionsColumnFamily,
    )

    self.created["bq_table"][bqt_name] = BigqueryTable(self, f"bqt_{bqt_name}", **bqt)


def create_bq_routine(self, bqr):
    "create bqr"
    bqr_name = bqr["routine_id"]
    bqr["dataset_id"] = self.tf_ref("dataset_id", bqr["dataset_id"])
    bqr["project"] = self.tf_ref("project", bqr["project"])
    self.tf_param_list(
        bqr,
        "arguments",
        BigqueryRoutineArguments,
    )

    self.created["bq_routine"][bqr_name] = BigqueryRoutine(
        self, f"bqr_{bqr_name}", **bqr
    )


def generate_bigquery_dataset(self, my_resource, resource):
    "create bigquery dataset"
    for vm in self.eztf_config.get(my_resource, []):
        create_bq_dataset(self, vm)


def generate_bigquery_table(self, my_resource, resource):
    "create bigquery table"
    for vm in self.eztf_config.get(my_resource, []):
        create_bq_table(self, vm)


def generate_bigquery_routine(self, my_resource, resource):
    "create bigquery routine"
    for vm in self.eztf_config.get(my_resource, []):
        create_bq_routine(self, vm)
