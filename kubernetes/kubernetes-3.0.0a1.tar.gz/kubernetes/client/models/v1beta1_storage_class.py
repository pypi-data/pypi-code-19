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


class V1beta1StorageClass(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, api_version=None, kind=None, metadata=None, parameters=None, provisioner=None):
        """
        V1beta1StorageClass - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'api_version': 'str',
            'kind': 'str',
            'metadata': 'V1ObjectMeta',
            'parameters': 'dict(str, str)',
            'provisioner': 'str'
        }

        self.attribute_map = {
            'api_version': 'apiVersion',
            'kind': 'kind',
            'metadata': 'metadata',
            'parameters': 'parameters',
            'provisioner': 'provisioner'
        }

        self._api_version = api_version
        self._kind = kind
        self._metadata = metadata
        self._parameters = parameters
        self._provisioner = provisioner

    @property
    def api_version(self):
        """
        Gets the api_version of this V1beta1StorageClass.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :return: The api_version of this V1beta1StorageClass.
        :rtype: str
        """
        return self._api_version

    @api_version.setter
    def api_version(self, api_version):
        """
        Sets the api_version of this V1beta1StorageClass.
        APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources

        :param api_version: The api_version of this V1beta1StorageClass.
        :type: str
        """

        self._api_version = api_version

    @property
    def kind(self):
        """
        Gets the kind of this V1beta1StorageClass.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :return: The kind of this V1beta1StorageClass.
        :rtype: str
        """
        return self._kind

    @kind.setter
    def kind(self, kind):
        """
        Sets the kind of this V1beta1StorageClass.
        Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds

        :param kind: The kind of this V1beta1StorageClass.
        :type: str
        """

        self._kind = kind

    @property
    def metadata(self):
        """
        Gets the metadata of this V1beta1StorageClass.
        Standard object's metadata. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata

        :return: The metadata of this V1beta1StorageClass.
        :rtype: V1ObjectMeta
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """
        Sets the metadata of this V1beta1StorageClass.
        Standard object's metadata. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#metadata

        :param metadata: The metadata of this V1beta1StorageClass.
        :type: V1ObjectMeta
        """

        self._metadata = metadata

    @property
    def parameters(self):
        """
        Gets the parameters of this V1beta1StorageClass.
        Parameters holds the parameters for the provisioner that should create volumes of this storage class.

        :return: The parameters of this V1beta1StorageClass.
        :rtype: dict(str, str)
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """
        Sets the parameters of this V1beta1StorageClass.
        Parameters holds the parameters for the provisioner that should create volumes of this storage class.

        :param parameters: The parameters of this V1beta1StorageClass.
        :type: dict(str, str)
        """

        self._parameters = parameters

    @property
    def provisioner(self):
        """
        Gets the provisioner of this V1beta1StorageClass.
        Provisioner indicates the type of the provisioner.

        :return: The provisioner of this V1beta1StorageClass.
        :rtype: str
        """
        return self._provisioner

    @provisioner.setter
    def provisioner(self, provisioner):
        """
        Sets the provisioner of this V1beta1StorageClass.
        Provisioner indicates the type of the provisioner.

        :param provisioner: The provisioner of this V1beta1StorageClass.
        :type: str
        """
        if provisioner is None:
            raise ValueError("Invalid value for `provisioner`, must not be `None`")

        self._provisioner = provisioner

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
        if not isinstance(other, V1beta1StorageClass):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
