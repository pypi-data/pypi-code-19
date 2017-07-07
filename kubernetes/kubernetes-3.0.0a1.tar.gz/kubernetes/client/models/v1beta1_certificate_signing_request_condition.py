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


class V1beta1CertificateSigningRequestCondition(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, last_update_time=None, message=None, reason=None, type=None):
        """
        V1beta1CertificateSigningRequestCondition - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'last_update_time': 'datetime',
            'message': 'str',
            'reason': 'str',
            'type': 'str'
        }

        self.attribute_map = {
            'last_update_time': 'lastUpdateTime',
            'message': 'message',
            'reason': 'reason',
            'type': 'type'
        }

        self._last_update_time = last_update_time
        self._message = message
        self._reason = reason
        self._type = type

    @property
    def last_update_time(self):
        """
        Gets the last_update_time of this V1beta1CertificateSigningRequestCondition.
        timestamp for the last update to this condition

        :return: The last_update_time of this V1beta1CertificateSigningRequestCondition.
        :rtype: datetime
        """
        return self._last_update_time

    @last_update_time.setter
    def last_update_time(self, last_update_time):
        """
        Sets the last_update_time of this V1beta1CertificateSigningRequestCondition.
        timestamp for the last update to this condition

        :param last_update_time: The last_update_time of this V1beta1CertificateSigningRequestCondition.
        :type: datetime
        """

        self._last_update_time = last_update_time

    @property
    def message(self):
        """
        Gets the message of this V1beta1CertificateSigningRequestCondition.
        human readable message with details about the request state

        :return: The message of this V1beta1CertificateSigningRequestCondition.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Sets the message of this V1beta1CertificateSigningRequestCondition.
        human readable message with details about the request state

        :param message: The message of this V1beta1CertificateSigningRequestCondition.
        :type: str
        """

        self._message = message

    @property
    def reason(self):
        """
        Gets the reason of this V1beta1CertificateSigningRequestCondition.
        brief reason for the request state

        :return: The reason of this V1beta1CertificateSigningRequestCondition.
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """
        Sets the reason of this V1beta1CertificateSigningRequestCondition.
        brief reason for the request state

        :param reason: The reason of this V1beta1CertificateSigningRequestCondition.
        :type: str
        """

        self._reason = reason

    @property
    def type(self):
        """
        Gets the type of this V1beta1CertificateSigningRequestCondition.
        request approval state, currently Approved or Denied.

        :return: The type of this V1beta1CertificateSigningRequestCondition.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this V1beta1CertificateSigningRequestCondition.
        request approval state, currently Approved or Denied.

        :param type: The type of this V1beta1CertificateSigningRequestCondition.
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")

        self._type = type

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
        if not isinstance(other, V1beta1CertificateSigningRequestCondition):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
