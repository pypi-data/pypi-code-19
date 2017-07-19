class DeployResult(object):
    def __init__(self, vm_name, vm_uuid, cloud_provider_resource_name, autoload, auto_delete, wait_for_ip, auto_power_off, deployed_app_attributes,
                 deployed_app_address):
        """
        :param str vm_name: The name of the virtual machine
        :param uuid vm_uuid: The UUID
        :param str cloud_provider_resource_name: The Cloud Provider resource name
        :param boolean auto_power_off:
        :param boolean wait_for_ip:
        :param boolean auto_delete:
        :param boolean autoload:
        :param [dict] deployed_app_attributes:
        :param str deployed_app_address:
        :return:
        """

        self.vm_name = vm_name
        self.vm_uuid = vm_uuid
        self.cloud_provider_resource_name = cloud_provider_resource_name
        self.auto_power_off = auto_power_off
        self.wait_for_ip = wait_for_ip
        self.auto_delete = auto_delete
        self.autoload = autoload
        self.deployed_app_attributes = deployed_app_attributes
        self.deployed_app_address = deployed_app_address
