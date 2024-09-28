from cdktf import TerraformHclModule
import util

def create_any_module(self, data, module_details, my_resource):
    module_id = data.get("_eztf_module_id", util.random_str(n=5))
    del data["_eztf_module_id"]
    args = {"variables": data, **module_details}
    name = f"{my_resource}_{module_id}"
    TerraformHclModule(self, name, **args)


def generate_any_module(self, my_resource, resource):
    """creates any module"""
    module_details = (
        self.eztf_config.get("eztf", {}).get("tf_any_module", {}).get(my_resource, {})
    )
    for data in self.eztf_config.get(my_resource, []):
        create_any_module(self, data,module_details, my_resource)
