# coding: utf-8

"""
    Kubernetes

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    OpenAPI spec version: v1.7.1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class V1PersistentVolumeClaimSpec(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, access_modes=None, resources=None, selector=None, storage_class_name=None, volume_name=None):
        """
        V1PersistentVolumeClaimSpec - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'access_modes': 'list[str]',
            'resources': 'V1ResourceRequirements',
            'selector': 'V1LabelSelector',
            'storage_class_name': 'str',
            'volume_name': 'str'
        }

        self.attribute_map = {
            'access_modes': 'accessModes',
            'resources': 'resources',
            'selector': 'selector',
            'storage_class_name': 'storageClassName',
            'volume_name': 'volumeName'
        }

        self._access_modes = access_modes
        self._resources = resources
        self._selector = selector
        self._storage_class_name = storage_class_name
        self._volume_name = volume_name

    @property
    def access_modes(self):
        """
        Gets the access_modes of this V1PersistentVolumeClaimSpec.
        AccessModes contains the desired access modes the volume should have. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes-1

        :return: The access_modes of this V1PersistentVolumeClaimSpec.
        :rtype: list[str]
        """
        return self._access_modes

    @access_modes.setter
    def access_modes(self, access_modes):
        """
        Sets the access_modes of this V1PersistentVolumeClaimSpec.
        AccessModes contains the desired access modes the volume should have. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#access-modes-1

        :param access_modes: The access_modes of this V1PersistentVolumeClaimSpec.
        :type: list[str]
        """

        self._access_modes = access_modes

    @property
    def resources(self):
        """
        Gets the resources of this V1PersistentVolumeClaimSpec.
        Resources represents the minimum resources the volume should have. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#resources

        :return: The resources of this V1PersistentVolumeClaimSpec.
        :rtype: V1ResourceRequirements
        """
        return self._resources

    @resources.setter
    def resources(self, resources):
        """
        Sets the resources of this V1PersistentVolumeClaimSpec.
        Resources represents the minimum resources the volume should have. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#resources

        :param resources: The resources of this V1PersistentVolumeClaimSpec.
        :type: V1ResourceRequirements
        """

        self._resources = resources

    @property
    def selector(self):
        """
        Gets the selector of this V1PersistentVolumeClaimSpec.
        A label query over volumes to consider for binding.

        :return: The selector of this V1PersistentVolumeClaimSpec.
        :rtype: V1LabelSelector
        """
        return self._selector

    @selector.setter
    def selector(self, selector):
        """
        Sets the selector of this V1PersistentVolumeClaimSpec.
        A label query over volumes to consider for binding.

        :param selector: The selector of this V1PersistentVolumeClaimSpec.
        :type: V1LabelSelector
        """

        self._selector = selector

    @property
    def storage_class_name(self):
        """
        Gets the storage_class_name of this V1PersistentVolumeClaimSpec.
        Name of the StorageClass required by the claim. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#class-1

        :return: The storage_class_name of this V1PersistentVolumeClaimSpec.
        :rtype: str
        """
        return self._storage_class_name

    @storage_class_name.setter
    def storage_class_name(self, storage_class_name):
        """
        Sets the storage_class_name of this V1PersistentVolumeClaimSpec.
        Name of the StorageClass required by the claim. More info: https://kubernetes.io/docs/concepts/storage/persistent-volumes#class-1

        :param storage_class_name: The storage_class_name of this V1PersistentVolumeClaimSpec.
        :type: str
        """

        self._storage_class_name = storage_class_name

    @property
    def volume_name(self):
        """
        Gets the volume_name of this V1PersistentVolumeClaimSpec.
        VolumeName is the binding reference to the PersistentVolume backing this claim.

        :return: The volume_name of this V1PersistentVolumeClaimSpec.
        :rtype: str
        """
        return self._volume_name

    @volume_name.setter
    def volume_name(self, volume_name):
        """
        Sets the volume_name of this V1PersistentVolumeClaimSpec.
        VolumeName is the binding reference to the PersistentVolume backing this claim.

        :param volume_name: The volume_name of this V1PersistentVolumeClaimSpec.
        :type: str
        """

        self._volume_name = volume_name

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        if not isinstance(other, V1PersistentVolumeClaimSpec):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
