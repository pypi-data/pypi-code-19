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


class V1beta1ReplicaSetCondition(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, last_transition_time=None, message=None, reason=None, status=None, type=None):
        """
        V1beta1ReplicaSetCondition - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'last_transition_time': 'datetime',
            'message': 'str',
            'reason': 'str',
            'status': 'str',
            'type': 'str'
        }

        self.attribute_map = {
            'last_transition_time': 'lastTransitionTime',
            'message': 'message',
            'reason': 'reason',
            'status': 'status',
            'type': 'type'
        }

        self._last_transition_time = last_transition_time
        self._message = message
        self._reason = reason
        self._status = status
        self._type = type

    @property
    def last_transition_time(self):
        """
        Gets the last_transition_time of this V1beta1ReplicaSetCondition.
        The last time the condition transitioned from one status to another.

        :return: The last_transition_time of this V1beta1ReplicaSetCondition.
        :rtype: datetime
        """
        return self._last_transition_time

    @last_transition_time.setter
    def last_transition_time(self, last_transition_time):
        """
        Sets the last_transition_time of this V1beta1ReplicaSetCondition.
        The last time the condition transitioned from one status to another.

        :param last_transition_time: The last_transition_time of this V1beta1ReplicaSetCondition.
        :type: datetime
        """

        self._last_transition_time = last_transition_time

    @property
    def message(self):
        """
        Gets the message of this V1beta1ReplicaSetCondition.
        A human readable message indicating details about the transition.

        :return: The message of this V1beta1ReplicaSetCondition.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Sets the message of this V1beta1ReplicaSetCondition.
        A human readable message indicating details about the transition.

        :param message: The message of this V1beta1ReplicaSetCondition.
        :type: str
        """

        self._message = message

    @property
    def reason(self):
        """
        Gets the reason of this V1beta1ReplicaSetCondition.
        The reason for the condition's last transition.

        :return: The reason of this V1beta1ReplicaSetCondition.
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """
        Sets the reason of this V1beta1ReplicaSetCondition.
        The reason for the condition's last transition.

        :param reason: The reason of this V1beta1ReplicaSetCondition.
        :type: str
        """

        self._reason = reason

    @property
    def status(self):
        """
        Gets the status of this V1beta1ReplicaSetCondition.
        Status of the condition, one of True, False, Unknown.

        :return: The status of this V1beta1ReplicaSetCondition.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this V1beta1ReplicaSetCondition.
        Status of the condition, one of True, False, Unknown.

        :param status: The status of this V1beta1ReplicaSetCondition.
        :type: str
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")

        self._status = status

    @property
    def type(self):
        """
        Gets the type of this V1beta1ReplicaSetCondition.
        Type of replica set condition.

        :return: The type of this V1beta1ReplicaSetCondition.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this V1beta1ReplicaSetCondition.
        Type of replica set condition.

        :param type: The type of this V1beta1ReplicaSetCondition.
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
        if not isinstance(other, V1beta1ReplicaSetCondition):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
