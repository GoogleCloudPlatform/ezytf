from imports.google.data_google_organization import DataGoogleOrganization


def data_google_org(self):
    self.ensure_variables(["organization_id"])
    self.created["data"]["google_org"] = DataGoogleOrganization(
        self, "org", organization=self.tf_ref("organization", "/")
    )
