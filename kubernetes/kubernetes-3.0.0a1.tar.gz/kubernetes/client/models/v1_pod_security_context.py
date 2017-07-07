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


class V1PodSecurityContext(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, fs_group=None, run_as_non_root=None, run_as_user=None, se_linux_options=None, supplemental_groups=None):
        """
        V1PodSecurityContext - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'fs_group': 'int',
            'run_as_non_root': 'bool',
            'run_as_user': 'int',
            'se_linux_options': 'V1SELinuxOptions',
            'supplemental_groups': 'list[int]'
        }

        self.attribute_map = {
            'fs_group': 'fsGroup',
            'run_as_non_root': 'runAsNonRoot',
            'run_as_user': 'runAsUser',
            'se_linux_options': 'seLinuxOptions',
            'supplemental_groups': 'supplementalGroups'
        }

        self._fs_group = fs_group
        self._run_as_non_root = run_as_non_root
        self._run_as_user = run_as_user
        self._se_linux_options = se_linux_options
        self._supplemental_groups = supplemental_groups

    @property
    def fs_group(self):
        """
        Gets the fs_group of this V1PodSecurityContext.
        A special supplemental group that applies to all containers in a pod. Some volume types allow the Kubelet to change the ownership of that volume to be owned by the pod:  1. The owning GID will be the FSGroup 2. The setgid bit is set (new files created in the volume will be owned by FSGroup) 3. The permission bits are OR'd with rw-rw----  If unset, the Kubelet will not modify the ownership and permissions of any volume.

        :return: The fs_group of this V1PodSecurityContext.
        :rtype: int
        """
        return self._fs_group

    @fs_group.setter
    def fs_group(self, fs_group):
        """
        Sets the fs_group of this V1PodSecurityContext.
        A special supplemental group that applies to all containers in a pod. Some volume types allow the Kubelet to change the ownership of that volume to be owned by the pod:  1. The owning GID will be the FSGroup 2. The setgid bit is set (new files created in the volume will be owned by FSGroup) 3. The permission bits are OR'd with rw-rw----  If unset, the Kubelet will not modify the ownership and permissions of any volume.

        :param fs_group: The fs_group of this V1PodSecurityContext.
        :type: int
        """

        self._fs_group = fs_group

    @property
    def run_as_non_root(self):
        """
        Gets the run_as_non_root of this V1PodSecurityContext.
        Indicates that the container must run as a non-root user. If true, the Kubelet will validate the image at runtime to ensure that it does not run as UID 0 (root) and fail to start the container if it does. If unset or false, no such validation will be performed. May also be set in SecurityContext.  If set in both SecurityContext and PodSecurityContext, the value specified in SecurityContext takes precedence.

        :return: The run_as_non_root of this V1PodSecurityContext.
        :rtype: bool
        """
        return self._run_as_non_root

    @run_as_non_root.setter
    def run_as_non_root(self, run_as_non_root):
        """
        Sets the run_as_non_root of this V1PodSecurityContext.
        Indicates that the container must run as a non-root user. If true, the Kubelet will validate the image at runtime to ensure that it does not run as UID 0 (root) and fail to start the container if it does. If unset or false, no such validation will be performed. May also be set in SecurityContext.  If set in both SecurityContext and PodSecurityContext, the value specified in SecurityContext takes precedence.

        :param run_as_non_root: The run_as_non_root of this V1PodSecurityContext.
        :type: bool
        """

        self._run_as_non_root = run_as_non_root

    @property
    def run_as_user(self):
        """
        Gets the run_as_user of this V1PodSecurityContext.
        The UID to run the entrypoint of the container process. Defaults to user specified in image metadata if unspecified. May also be set in SecurityContext.  If set in both SecurityContext and PodSecurityContext, the value specified in SecurityContext takes precedence for that container.

        :return: The run_as_user of this V1PodSecurityContext.
        :rtype: int
        """
        return self._run_as_user

    @run_as_user.setter
    def run_as_user(self, run_as_user):
        """
        Sets the run_as_user of this V1PodSecurityContext.
        The UID to run the entrypoint of the container process. Defaults to user specified in image metadata if unspecified. May also be set in SecurityContext.  If set in both SecurityContext and PodSecurityContext, the value specified in SecurityContext takes precedence for that container.

        :param run_as_user: The run_as_user of this V1PodSecurityContext.
        :type: int
        """

        self._run_as_user = run_as_user

    @property
    def se_linux_options(self):
        """
        Gets the se_linux_options of this V1PodSecurityContext.
        The SELinux context to be applied to all containers. If unspecified, the container runtime will allocate a random SELinux context for each container.  May also be set in SecurityContext.  If set in both SecurityContext and PodSecurityContext, the value specified in SecurityContext takes precedence for that container.

        :return: The se_linux_options of this V1PodSecurityContext.
        :rtype: V1SELinuxOptions
        """
        return self._se_linux_options

    @se_linux_options.setter
    def se_linux_options(self, se_linux_options):
        """
        Sets the se_linux_options of this V1PodSecurityContext.
        The SELinux context to be applied to all containers. If unspecified, the container runtime will allocate a random SELinux context for each container.  May also be set in SecurityContext.  If set in both SecurityContext and PodSecurityContext, the value specified in SecurityContext takes precedence for that container.

        :param se_linux_options: The se_linux_options of this V1PodSecurityContext.
        :type: V1SELinuxOptions
        """

        self._se_linux_options = se_linux_options

    @property
    def supplemental_groups(self):
        """
        Gets the supplemental_groups of this V1PodSecurityContext.
        A list of groups applied to the first process run in each container, in addition to the container's primary GID.  If unspecified, no groups will be added to any container.

        :return: The supplemental_groups of this V1PodSecurityContext.
        :rtype: list[int]
        """
        return self._supplemental_groups

    @supplemental_groups.setter
    def supplemental_groups(self, supplemental_groups):
        """
        Sets the supplemental_groups of this V1PodSecurityContext.
        A list of groups applied to the first process run in each container, in addition to the container's primary GID.  If unspecified, no groups will be added to any container.

        :param supplemental_groups: The supplemental_groups of this V1PodSecurityContext.
        :type: list[int]
        """

        self._supplemental_groups = supplemental_groups

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
        if not isinstance(other, V1PodSecurityContext):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
