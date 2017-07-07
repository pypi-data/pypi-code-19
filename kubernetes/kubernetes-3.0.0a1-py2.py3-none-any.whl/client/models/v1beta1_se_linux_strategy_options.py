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


class V1beta1SELinuxStrategyOptions(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, rule=None, se_linux_options=None):
        """
        V1beta1SELinuxStrategyOptions - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'rule': 'str',
            'se_linux_options': 'V1SELinuxOptions'
        }

        self.attribute_map = {
            'rule': 'rule',
            'se_linux_options': 'seLinuxOptions'
        }

        self._rule = rule
        self._se_linux_options = se_linux_options

    @property
    def rule(self):
        """
        Gets the rule of this V1beta1SELinuxStrategyOptions.
        type is the strategy that will dictate the allowable labels that may be set.

        :return: The rule of this V1beta1SELinuxStrategyOptions.
        :rtype: str
        """
        return self._rule

    @rule.setter
    def rule(self, rule):
        """
        Sets the rule of this V1beta1SELinuxStrategyOptions.
        type is the strategy that will dictate the allowable labels that may be set.

        :param rule: The rule of this V1beta1SELinuxStrategyOptions.
        :type: str
        """
        if rule is None:
            raise ValueError("Invalid value for `rule`, must not be `None`")

        self._rule = rule

    @property
    def se_linux_options(self):
        """
        Gets the se_linux_options of this V1beta1SELinuxStrategyOptions.
        seLinuxOptions required to run as; required for MustRunAs More info: https://git.k8s.io/community/contributors/design-proposals/security_context.md

        :return: The se_linux_options of this V1beta1SELinuxStrategyOptions.
        :rtype: V1SELinuxOptions
        """
        return self._se_linux_options

    @se_linux_options.setter
    def se_linux_options(self, se_linux_options):
        """
        Sets the se_linux_options of this V1beta1SELinuxStrategyOptions.
        seLinuxOptions required to run as; required for MustRunAs More info: https://git.k8s.io/community/contributors/design-proposals/security_context.md

        :param se_linux_options: The se_linux_options of this V1beta1SELinuxStrategyOptions.
        :type: V1SELinuxOptions
        """

        self._se_linux_options = se_linux_options

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
        if not isinstance(other, V1beta1SELinuxStrategyOptions):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
