# -*- coding: utf-8 -*-
import os, csv, json, copy
import requests
import base64
import urllib3
from pytz import timezone
import datetime
from collections import OrderedDict
from hssadmin.admincore import APIParameters
urllib3.disable_warnings()

"""
Cloudian HyperStore Admin API SDK
"""

class adminClient():
    """
    This Class definition is to create a Python object having some methods that *Cloudian HyperStore(R)* **Admin APIs** are wrapped and properties.
    You need to specify the arguments in the table below to create the object using this class definition.

    .. csv-table:: Arguments for initialization of this class definition
        :header: "Argument name", "Type", "Mandatory/Optional", "Default value"
        :widths: 25, 15, 15, 20

        "base_url", "string", "Mandatory", ""
        "enable_auth", "bool", "Optional", "True"
        "user", "string", "Optional", "sysadmin"
        "passwd", "string", "Optional", "public"

    The **adminClient** object has the following methods and properties.

    .. csv-table:: Methods and Properties
        :header: "Type", "Name", "Category"
        :widths: 10, 30, 25

        "Method", "user_add", "User Management"
        "Method", "userpasswd_set", "User Management"
        "Method", "user_delete", "User Management"
        "Method", "user_deactivate", "User Management"
        "Method", "user_activate", "User Management"
        "Method", "user_list", "User Management"
        "Method", "users_list", "User Management"
        "Method", "s3credential_add", "User Management"
        "Method", "s3credentials_all_list", "User Management"
        "Method", "s3credentials_active_list", "User Management"
        "Method", "s3credential_import", "User Management"
        "Method", "accesskey_deactivate", "User Management"
        "Method", "accesskey_activate", "User Management"
        "Method", "secretkey_list", "User Management"
        "Method", "user_ratingplan_list", "User Management"
        "Method", "user_ratingplanid_list", "User Management"
        "Method", "user_ratingplanid_set", "User Management"
        "Method", "group_add", "Group Management"
        "Method", "group_delete", "Group Management"
        "Method", "group_deactivate", "Group Management"
        "Method", "group_activate", "Group Management"
        "Method", "group_list", "Group Management"
        "Method", "groups_list", "Group Management"
        "Method", "group_ratingplanid_list", "Group Management"
        "Method", "group_ratingplanid_set", "Group Management"
        "Method", "storpol_list", "Storage Policies"
        "Method", "storpols_list", "Storage Policies"
        "Method", "storpolid_list", "Storage Policies"
        "Method", "storpol_status_change", "Storage Policies"
        "Method", "storpol_usage", "Storage Policies"
        "Method", "qos_set", "Quality of Service"
        "Method", "qos_unset", "Quality of Service"
        "Method", "qos_list", "Quality of Service"
        "Method", "usagereport_list", "Usage Reporting"
        "Method", "hss_info", "System Services"
        "Method", "license_info", "System Services"
        "Method", "sys_version", "System Services"
        "Method", "node_list", "System Monitoring"
        "Method", "node_monitoring_data", "System Monitoring"
        "Method", "region_monitoring_data", "System Monitoring"
        "Property", "base_url", ""
        "Property", "encrypted_passwd", ""
    .. note::
        For detailed usage of each method, refer to the section below corresponding to the method you want to know.

    """
    def __init__(self, base_url, enable_auth=True, user="sysadmin", passwd="public"):
        """
        Initialize Admin Client object

        :param base_url: Admin API endpoint url
        :param enable_auth: Enable or disable basic authentication (default: ``True``)
        :param auth_user: Admin API authentication user (default: ``sysadmin``)
        :param passwd: Admin API authentication password (default: ``public``)
        :type base_url: string
        :type auth_user: string
        :type passwd: string
        :return: Admin Client object
        :rtype: instance
        """
        self.__base_url = base_url
        self.__enable_auth = enable_auth
        self.__auth_user = user
        self.__passwd = passwd

        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        if self.__enable_auth:
            self.__base64string = base64.encodestring(('%s:%s' % (self.__auth_user, self.__passwd)).encode("utf-8"))[:-1]
            self.headers["Authorization"] = "Basic %s" % self.__base64string.decode("utf-8")

    @property
    def base_url(self):
        return self.__base_url
    @base_url.setter
    def base_url(self, base_url):
        self.__base_url = base_url

    @property
    def encrypted_passwd(self):
        return self.__base64string

    # User Management
    def user_add(self, usr_params={}, file=None):
        # PUT New User
        '''
        **Add new CMC users**

        You can add new CMC user(s) using this method.
        If you set the CSV filename described the UserInfo as the "``file=``" argument, you can register many users in bulk.

        :download:`Sample CSV file for user batch registration <cmc_user_info.csv>`

        .. warning::
            If you set the "file=" argument, all other arguments are ignored.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**userType**", "**mandatory**"
            "fullName", "optional"
            "emailAddr", "optional"
            "address1", "optional"
            "address2", "optional"
            "city", "optional"
            "state", "optional"
            "zip", "optional"
            "country", "optional"
            "phone", "optional"
            "**groupId**", "**mandatory**"
            "website", "optional"
            "active", "optional"
            "canonicalUserId", "optional"

        Or.....

        :param file: CSV file for user batch registration
        :type file: string
        :return: Number of successes and failures of this user add operation
        :rtype: string
        :example: user_add(file='cmc_user_info.csv')
        '''
        url = self.base_url + "user"
        method = "PUT"
        def_params = APIParameters.p_user_info

        success_count = 0
        fail_count = 0
        fail_objects = []
        if file and os.path.isfile(file):
            with open(file, 'rt') as f:
                usr_params = {}
                for row in csv.DictReader(f):
                    usr_params = row
                    return_val = self.__call_admin_api(url, method, def_params, usr_params)
                    if int(return_val.status_code) == 200:
                        success_count += 1
                    else:
                        fail_objects.append(row['userId'])
                        fail_count += 1
        elif usr_params:
            return_val = self.__call_admin_api(url, method, def_params, usr_params)
            if int(return_val.status_code) == 200:
                success_count +=1
            else:
                fail_objects.append(row['userId'])
                fail_count += 1

        if fail_objects:
            fail_objects = ",".join(fail_objects)
            return "{0} user add operations succeeded and {1} failed ({2}).".format(success_count, fail_count, fail_objects)
        else:
            return "{0} user add operations succeeded.".format(success_count)

    def userpasswd_set(self, usr_params={}, file=None):
        # POST User's CMC Password
        '''
        **Set password to a CMC user**

        You can set password to CMC user(s) using this method.
        If you set the CSV filename described the UserInfo as the "``file=``" argument, you can set password to many users in bulk.

        .. warning::
            If you set the "file=" argument, all other arguments are ignored.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "**password**", "**mandatory**"

        Or.....

        :param file: CSV file for user batch registration
        :type file: string
        :return: Status of the CMC user password set operations
        :rtype: string
        :example: userpasswd_set(file='cmc_user_info.csv')
        '''
        url = self.base_url + "user/password?"
        method = "POST"
        def_params = APIParameters.p_userpasswd_set

        success_count = 0
        fail_count = 0
        fail_objects = []
        if file and os.path.isfile(file):
            with open(file, 'rt') as f:
                usr_params = {}
                for row in csv.DictReader(f):
                    if row['password']:
                        usr_params = row
                        return_val = self.__call_admin_api(url, method, def_params, usr_params)
                        if int(return_val.status_code) == 200:
                            success_count += 1
                        else:
                            fail_objects.append(row['userId'])
                            fail_count += 1
        elif usr_params:
            return_val = self.__call_admin_api(url, method, def_params, usr_params)
            if int(return_val.status_code) == 200:
                success_count +=1
            else:
                fail_objects.append(row['userId'])
                fail_count += 1

        if fail_objects:
            fail_objects = ",".join(fail_objects)
            return "{0} user password set operations succeeded and {1} failed ({2}).".format(success_count, fail_count, fail_objects)
        else:
            return "{0} user password set operations succeeded.".format(success_count)

    def user_delete(self,
                    usr_params={},
                    file=None,
                    userId=None,
                    groupId=None,
                    deactive_only=True):
        # DELETE User
        '''
        **Delete CMC users**

        You can delete existing CMC user(s) using this method.

        .. note::
            By default, this function deletes the "deactive" CMC users only.
            If you want to delete "active" CMC users, please set the "deactive_only" parameter to "False".

        .. warning::
            If you set the "file=" argument, all other arguments are ignored.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"

        Or.....

        :param file: CSV file for user batch registration
        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param deactive_only: whether or not to be deleted deactivated users only (default: ``True``)
        :type file: string
        :type userId: string
        :type groupId: string
        :type deactive_only: boolean
        :return: Status of CMC user delete operations
        :rtype: string
        :example: user_delete(userId="gzuser4", groupId="GROUP-Z")
        '''
        url = self.base_url + "user?"
        method = "DELETE"
        def_params = APIParameters.p_user_delete

        success_count = 0
        fail_count = 0
        fail_objects = []
        if file and os.path.isfile(file):
            with open(file, 'rt') as f:
                usr_params = {}
                for row in csv.DictReader(f):
                    usr_params["userId"] = row['userId']
                    usr_params["groupId"] = row['groupId']

                    cp_usr_params = copy.deepcopy(usr_params)
                    user_status = self.user_list(cp_usr_params).get('active')
                    if user_status == "true":
                        active = True
                    elif user_status == "false":
                        active = False
                    elif user_status == None:
                        active = None

                    if (deactive_only == True and active == False) or (deactive_only == False):
                        return_val = self.__call_admin_api(url, method, def_params, usr_params)
                        if int(return_val.status_code) == 200:
                            success_count += 1
                        else:
                            fail_objects.append(row['userId'])
                            fail_count += 1
        elif usr_params:
            cp_usr_params = copy.deepcopy(usr_params)
            user_status = self.user_list(cp_usr_params).get('active')
            if user_status == "true":
                active = True
            elif user_status == "false":
                active = False
            elif user_status == None:
                active = None

            if (deactive_only == True and active == False) or (deactive_only == False):
                return_val = self.__call_admin_api(url, method, def_params, usr_params)
                if int(return_val.status_code) == 200:
                    success_count +=1
                else:
                    fail_objects.append(row['userId'])
                    fail_count += 1
        elif (not usr_params and not file) and (userId and groupId):
            usr_params["userId"] = userId
            usr_params["groupId"] = groupId

            cp_usr_params = copy.deepcopy(usr_params)
            user_status = self.user_list(cp_usr_params).get('active')
            if user_status == "true":
                active = True
            elif user_status == "false":
                active = False
            elif user_status == None:
                active = None

            if (deactive_only == True and active == False) or (deactive_only == False):
                return_val = self.__call_admin_api(url, method, def_params, usr_params)
                if int(return_val.status_code) == 200:
                    success_count += 1
                else:
                    fail_objects.append(row['userId'])
                    fail_count += 1

        if fail_objects:
            fail_objects = ",".join(fail_objects)
            msg = "{0} user delete operations succeeded and {1} failed ({2}).".format(success_count, fail_count, fail_objects)
        else:
            msg = "{0} user delete operations succeeded.".format(success_count)

        usr_params.clear()
        return msg

    def user_deactivate(self,
                        usr_params={},
                        userId=None,
                        groupId=None,
                        userType="User"):
        # POST Updated User
        '''
        **Deactivate a CMC user**

        You can make a CMC user's status "deactive" using this method.

        .. note::
            By default, you can deactivate the CMC users with "User" type only.
            If you want to deactivate different types of user, set the "userType=" argument.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**userType**", "**mandatory**"
            "fullName", "optional"
            "emailAddr", "optional"
            "address1", "optional"
            "address2", "optional"
            "city", "optional"
            "state", "optional"
            "zip", "optional"
            "country", "optional"
            "phone", "optional"
            "**groupId**", "**mandatory**"
            "website", "optional"
            "active", "optional"
            "canonicalUserId", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param userType: CMC user type (default: ``User``)
        :type userId: string
        :type groupId: string
        :type userType: string
        :return: Status of the CMC user deactivation operations
        :rtype: string
        :example: user_deactivate(userId="gzuser5", groupId="GROUP-Z")
        '''
        url = self.base_url + "user"
        method = "POST"
        def_params = APIParameters.p_user_info

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
        if userType == "GroupAdmin":
            usr_params['userType'] = "GroupAdmin"
        else:
            usr_params['userType'] = "User"
        usr_params['active'] = "False"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The user({0}) has been deactivated.".format(usr_params['userId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def user_activate(self,
                      usr_params={},
                      userId=None,
                      groupId=None,
                      userType="User"):
        # POST Updated User
        '''
        **Activate a CMC user**

        You can make a CMC user's status "active" using this method.

        .. note::
            By default, you can activate the CMC users with "User" type only.
            If you want to activate different types of user, set the "userType=" argument.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**userType**", "**mandatory**"
            "fullName", "optional"
            "emailAddr", "optional"
            "address1", "optional"
            "address2", "optional"
            "city", "optional"
            "state", "optional"
            "zip", "optional"
            "country", "optional"
            "phone", "optional"
            "**groupId**", "**mandatory**"
            "website", "optional"
            "active", "optional"
            "canonicalUserId", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param userType: CMC user type (default: ``User``)
        :type userId: string
        :type groupId: string
        :type userType: string
        :return: Status of the CMC user activation operations
        :rtype: string
        :example: user_activate(userId="gzuser5", groupId="GROUP-Z")
        '''
        url = self.base_url + "user"
        method = "POST"
        def_params = APIParameters.p_user_info

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
        if userType == "GroupAdmin":
            usr_params['userType'] = "GroupAdmin"
        else:
            usr_params['userType'] = "User"
        usr_params['active'] = "True"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The user({0}) has been activated.".format(usr_params['userId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def user_list(self, usr_params={}, userId=None, groupId=None):
        # GET User
        '''
        **List the specified CMC UserInfo**

        You can list the CMC UserInfo of a specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "**userType**", "**mandatory**"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :type userId: string
        :type groupId: string
        :return: UserInfo of a CMC user
        :rtype: dict
        :example: user_list(userId="gzuser5", groupId="GROUP-Z")
        '''
        url = self.base_url + "user?"
        method = "GET"
        def_params = APIParameters.p_user_list

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = {}

        usr_params.clear()
        return msg

    def users_list(self,
                   usr_params={},
                   groupId=None,
                   userType="all",
                   userStatus="active",
                   prefix=None,
                   limit=None,
                   offset=None):
        # GET User List
        '''
        **List some of the CMC UserInfo specified CMC group**

        You can list the CMC UserInfo of a specified **group** using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "**userType**", "**mandatory**"
            "**userStatus**", "**mandatory**"
            "prefix", "optional"
            "limit", "optional"
            "offset", "optional"

        Or.....

        :param groupId: CMC group ID
        :param userType: CMC user type (default: ``all``)
        :param userStatus: CMC user status (default: ``active``)
        :param prefix: Prefix (optional)
        :param limit: Limit (optional)
        :param offset: Offset (optional)
        :type groupId: string
        :type userType: string
        :type userStatus: string
        :type prefix: string
        :type limit: string
        :type offset: string
        :return: UserInfo of a CMC users belonging to a group
        :rtype: list
        :example: users_list(groupId="GROUP-Z", userStatus="inactive")
        '''
        url = self.base_url + "user/list?"
        method = "GET"
        def_params = APIParameters.p_users_list

        if not usr_params and groupId:
            usr_params['groupId'] = groupId
            usr_params['userType'] = userType
            usr_params['userType'] = userType
            usr_params['userStatus'] = userStatus
            if prefix:
                usr_params['prefix'] = prefix
            if limit:
                usr_params['limit'] = limit
            if offset:
                usr_params['offset'] = offset

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = []

        usr_params.clear()
        return msg

    def s3credential_add(self, usr_params={}, userId=None, groupId=None):
        # PUT User's New S3 Credential
        '''
        **Add a new S3 credential to the specified CMC user**

        You can add a new S3 credential to a specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :type userId: string
        :type groupId: string
        :return: Status of the S3 credential add operation
        :rtype: string
        :example: s3credential_add(userId="gzuser1", groupId="GROUP-Z")
        '''
        url = self.base_url + "user/credentials?"
        method = "PUT"
        def_params = APIParameters.p_s3cred_add

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        elif int(return_val.status_code) == 400:
            msg = "The user({0}) does not exist.".format(usr_params['userId'])
        elif int(return_val.status_code) == 403:
            msg = "Reached maximum number of credentials allowed."
        else:
            msg = ""

        usr_params.clear()
        return msg

    def s3credentials_all_list(self, usr_params={}, userId=None, groupId=None):
        # GET User's S3 Credentials List
        '''
        **List all S3 credentials of the specified CMC user**

        You can list all S3 credentials of the specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :type userId: string
        :type groupId: string
        :return: S3 credentials information of a CMC user
        :rtype: list
        :example: s3credentials_all_list(userId="gzuser1", groupId="GROUP-Z")
        '''
        url = self.base_url + "user/credentials/list?"
        method = "GET"
        def_params = APIParameters.p_s3creds_list

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = []

        usr_params.clear()
        return msg

    def s3credentials_active_list(self, usr_params={}, userId=None, groupId=None):
        # GET User's S3 Credentials List (Active)
        '''
        **List active S3 credentials of the specified CMC user**

        You can list active S3 credentials of the specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :type userId: string
        :type groupId: string
        :return: Only active S3 credentials information of a CMC user
        :rtype: list
        :example: s3credentials_active_list(userId="gzuser8", groupId="GROUP-Z")
        '''
        url = self.base_url + "user/credentials/list/active?"
        method = "GET"
        def_params = APIParameters.p_s3creds_list

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = []

        usr_params.clear()
        return msg

    def s3credential_import(self,
                            usr_params={},
                            userId=None,
                            groupId=None,
                            accessKey=None,
                            secretKey=None):
        # POST User's S3 Credential
        '''
        **import an S3 credential into the specified CMC user**

        You can import an S3 credential into the specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "**accessKey**", "**mandatory**"
            "**secretKey**", "**mandatory**"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param accessKey: S3 access key
        :param secretKey: S3 secret Key
        :type userId: string
        :type groupId: string
        :type accessKey: string
        :type secretKey: string
        :return: Status of the S3 credential import operation
        :rtype: string
        :example: s3credential_import(userId="gzuser8", groupId="GROUP-Z", accessKey="2596b3dd92f86a466c3d", secretKey="Pmy4HPi9uF5FSlABturX/o6HiB0U5n74Mivy/VFu")
        '''
        url = self.base_url + "user/credentials?"
        method = "POST"
        def_params = APIParameters.p_s3cred_imp

        if not usr_params and (userId and groupId and accessKey and secretKey):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
            usr_params['accessKey'] = accessKey
            usr_params['secretKey'] = secretKey

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The S3 credential({0}/{1}) was successfully imported.".format(usr_params['accessKey'], usr_params['secretKey'])
        elif int(return_val.status_code) == 400:
            msg = "The user({0}) does not exit.".format(usr_params['userId'])
        elif int(return_val.status_code) == 403:
            msg = "Reached maximum number of credentials allowed."
        elif int(return_val.status_code) == 409:
            msg = "The access key({0}) already exists.".format(usr_params['accessKey'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def accesskey_deactivate(self, usr_params={}, accessKey=None):
        # POST User's S3 Credential Status
        '''
        **Deactivate an S3 access key**

        You can make an S3 access key "deactive" using this method.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**accessKey**", "**mandatory**"
            "isActive", "optional"

        Or.....

        :param accessKey: S3 access key
        :type accessKey: string
        :return: Status of the S3 access key deactivation operation
        :rtype: string
        :example: accesskey_deactivate(accessKey="2596b3dd92f86a466c3d")
        '''
        url = self.base_url + "user/credentials/status?"
        method = "POST"
        def_params = APIParameters.p_accesskey_status

        if not usr_params and accessKey:
            usr_params['accessKey'] = accessKey
        usr_params['isActive'] = "false"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The access key({0}) has been deactivated.".format(usr_params['accessKey'])
        elif int(return_val.status_code) == 400:
            msg = "The access key({0}) is invalid.".format(usr_params['accessKey'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def accesskey_activate(self, usr_params={}, accessKey=None):
        # POST User's S3 Credential Status
        '''
        **Activate an S3 access key**

        You can make an S3 access key "active" using this method.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**accessKey**", "**mandatory**"
            "isActive", "optional"

        Or.....

        :param accessKey: S3 access key (default: ``None``)
        :type accessKey: string
        :return: Status of the S3 access key activation operation
        :rtype: string
        :example: accesskey_activate(accessKey="2596b3dd92f86a466c3d")
        '''
        url = self.base_url + "user/credentials/status?"
        method = "POST"
        def_params = APIParameters.p_accesskey_status

        if not usr_params and accessKey:
            usr_params['accessKey'] = accessKey
        usr_params['isActive'] = "true"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The access key({0}) has been activated.".format(usr_params['accessKey'])
        elif int(return_val.status_code) == 400:
            msg = "The access key({0}) is invalid.".format(usr_params['accessKey'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def secretkey_list(self, usr_params={}, accessKey=None):
        # GET User's S3 Credential
        '''
        **List a S3 secret key**

        You can list the secret key corresponding to the access key you specified using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**accessKey**", "**mandatory**"

        Or.....

        :param accessKey: S3 access key
        :type accessKey: string
        :return: S3 secret key
        :rtype: string
        :example: secretkey_list(accessKey="2596b3dd92f86a466c3d")
        '''
        url = self.base_url + "user/credentials?"
        method = "GET"
        def_params = APIParameters.p_secretkey_list

        if not usr_params and accessKey:
            usr_params['accessKey'] = accessKey

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            return_val = json.loads(return_val.text)
            if return_val['active'] == True and return_val['expireDate'] == None:
                msg = return_val['secretKey']
        elif int(return_val.status_code) == 204:
            msg = "The secret key corresponding to the access key({0}) could not be found.".format(usr_params['accessKey'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def user_ratingplan_list(self,
                             usr_params={},
                             userId=None,
                             groupId=None,
                             region=None):
        # GET User's Rating Plan
        '''
        **List rating plans for users**

        You can list rating plans for users using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param region: Region name (optional)
        :type userId: string
        :type groupId: string
        :type region: string
        :return: S3 rating plans for users
        :rtype: dict
        :example: user_ratingplan_list(userId="gzuser5", groupId="GROUP-Z")
        '''
        url = self.base_url + "user/ratingPlan?"
        method = "GET"
        def_params = APIParameters.p_user_ratingplan_info

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        elif int(return_val.status_code) == 204:
            msg = "Rating plan does not exist."
        else:
            msg = {}

        usr_params.clear()
        return msg

    def user_ratingplanid_list(self,
                               usr_params={},
                               userId=None,
                               groupId=None,
                               region=None):
        # GET User's Rating Plan ID
        '''
        **List a rating plan ID assigned to the specified user**

        You can list a rating plan ID to be assigned to the specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param region: Region name (optional)
        :type userId: string
        :type groupId: string
        :type region: string
        :return: S3 rating plan ID
        :rtype: string
        :example: user_ratingplanid_list(userId="gzuser5", groupId="GROUP-Z")
        '''
        url = self.base_url + "user/ratingPlanId?"
        method = "GET"
        def_params = APIParameters.p_user_ratingplan_info
        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = return_val.text
        else:
            msg = ""

        usr_params.clear()
        return msg

    def user_ratingplanid_set(self,
                              usr_params={},
                              userId=None,
                              groupId=None,
                              ratingPlanId=None,
                              region=None):
        # POST User's Rating Plan ID
        '''
        **Set a rating plan ID to the specified user**

        You can set a rating plan ID to the specified user using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "**ratingPlanId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param ratingPlanId: Rating Plan ID
        :param region: Region name (optional)
        :type userId: string
        :type groupId: string
        :type ratingPlanId: string
        :type region: string
        :return: Status of the rating plan id set operation
        :rtype: string
        :example: user_ratingplanid_set(userId="gzuser13", groupId="GROUP-Z", ratingPlanId="API-TEST-RP")
        '''
        url = self.base_url + "user/ratingPlanId?"
        method = "POST"
        def_params = APIParameters.p_user_ratingplanid_info

        if not usr_params and (userId and groupId and ratingPlanId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
            usr_params['ratingPlanId'] = ratingPlanId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The rating plan(ID: {0}) was assinged to the user({1}/{2}).".format(usr_params['ratingPlanId'], usr_params['groupId'], usr_params['userId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    # Group Management
    def group_add(self,
                  usr_params={},
                  file=None,
                  groupId=None,
                  groupName=None,
                  ldapGroup=None,
                  active=None):
        # PUT New Group
        '''
        **Add new CMC groups**

        You can add new CMC group(s) using this method.
        If you set the CSV filename described the GroupInfo as the "``file=``" argument, you can register many groups in bulk.

        :download:`Sample CSV file for group batch registration <cmc_group_info.csv>`

        .. warning::
            If you set the "file=" argument, all other arguments are ignored.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "groupName", "optional"
            "ldapGroup", "optional"
            "active", "optional"

        Or.....

        :param file: CSV file for group batch registration
        :param groupId: CMC group ID
        :param groupName: CMC group name
        :param ldapGroup: LDAP/AD group
        :param active: status of CMC group
        :type file: string
        :type groupId: string
        :type groupName: string
        :type ldapGroup: string
        :type active: bool
        :return: Number of successes and failures of this user add operation
        :rtype: string
        :example: group_add(file='cmc_group_info.csv')
        '''
        url = self.base_url + "group"
        method = "PUT"
        def_params = APIParameters.p_group_info

        success_count = 0
        fail_count = 0
        fail_objects = []
        if file and os.path.isfile(file):
            with open(file, 'rt') as f:
                usr_params = {}
                for row in csv.DictReader(f):
                    usr_params = row
                    return_val = self.__call_admin_api(url, method, def_params, usr_params)
                    if int(return_val.status_code) == 200:
                        success_count += 1
                    else:
                        fail_objects.append(row['groupId'])
                        fail_count += 1
        elif usr_params:
            return_val = self.__call_admin_api(url, method, def_params, usr_params)
            if int(return_val.status_code) == 200:
                success_count +=1
            else:
                fail_objects.append(row['groupId'])
                fail_count += 1
        elif not usr_params and groupId:
            usr_params['groupId'] = groupId
            if groupName:
                usr_params['groupName'] = groupName
            if ldapGroup:
                usr_params['ldapGroup'] = ldapGroup
            if active:
                usr_params['active'] = active
            return_val = self.__call_admin_api(url, method, def_params, usr_params)
            if int(return_val.status_code) == 200:
                success_count +=1
            else:
                fail_objects.append(row['groupId'])
                fail_count += 1

        if fail_objects:
            fail_objects = ",".join(fail_objects)
            msg = "{0} group add operations succeeded and {1} failed.\nFAILED: {2}".format(success_count, fail_count, fail_objects)
        else:
            msg = "{0} group add operations succeeded.".format(success_count)

        usr_params.clear()
        return msg

    def group_delete(self, usr_params={}, file=None, groupId=None):
        # DELETE Group
        '''
        **Delete CMC groups**

        You can delete existing CMC group(s) using this method.

        .. warning::
            If you set the "file=" argument, all other arguments are ignored.

        :param usr_params: Python dictionary to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"

        Or.....

        :param file: CSV file for group batch registration
        :param groupId: CMC group ID
        :type file: string
        :type groupId: string
        :return: Status of CMC group delete operations
        :rtype: string
        :example: group_delete(groupId="GROUP-Z")
        '''
        url = self.base_url + "group?"
        method = "DELETE"
        def_params = {"groupId": "mandatory"}

        success_count = 0
        fail_count = 0
        fail_objects = []
        if file and os.path.isfile(file):
            with open(file, 'rt') as f:
                usr_params = {}
                for row in csv.DictReader(f):
                    usr_params = row
                    return_val = self.__call_admin_api(url, method, def_params, usr_params)
                    if int(return_val.status_code) == 200:
                        success_count += 1
                    else:
                        fail_objects.append(row['groupId'])
                        fail_count += 1
        elif usr_params:
            return_val = self.__call_admin_api(url, method, def_params, usr_params)
            if int(return_val.status_code) == 200:
                success_count +=1
            else:
                fail_objects.append(row['groupId'])
                fail_count += 1
        elif not usr_params and groupId:
            usr_params['groupId'] = groupId
            return_val = self.__call_admin_api(url, method, def_params, usr_params)
            if int(return_val.status_code) == 200:
                success_count +=1
            else:
                fail_objects.append(row['groupId'])
                fail_count += 1

        if fail_objects:
            fail_objects = ",".join(fail_objects)
            msg = "{0} group delete operations succeeded and {1} failed.\nFAILED: {2}".format(success_count, fail_count, fail_objects)
        else:
            msg = "{0} group delete operations succeeded.".format(success_count)

        usr_params.clear()
        return msg

    def group_deactivate(self, usr_params={}, groupId=None):
        # POST Updated Group
        '''
        **Deactivate a CMC group**

        You can make a CMC group's status "deactive" using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "groupName", "optional"
            "ldapGroup", "optional"
            "active", "optional"

        Or.....

        :param groupId: CMC group ID
        :type groupId: string
        :return: Status of the CMC group deactivation operations
        :rtype: string
        :example: group_deactivate(groupId="GROUP-Z")
        '''
        url = self.base_url + "group"
        method = "POST"
        def_params = APIParameters.p_group_info

        if not usr_params and groupId:
            usr_params['groupId'] = groupId
        usr_params['active'] = "False"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The group({0}) has been deactivated.".format(usr_params['groupId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def group_activate(self, usr_params={}, groupId=None):
        # POST Updated Group
        '''
        **Activate a CMC group**

        You can make a CMC group's status "active" using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "groupName", "optional"
            "ldapGroup", "optional"
            "active", "optional"

        Or.....

        :param groupId: CMC group ID
        :type groupId: string
        :return: Status of the CMC group activation operations
        :rtype: string
        :example: user_activate(userId="gzuser5", groupId="GROUP-Z")
        '''
        url = self.base_url + "group"
        method = "POST"
        def_params = APIParameters.p_group_info

        if not usr_params and groupId:
            usr_params['groupId'] = groupId
        usr_params['active'] = "True"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The group({0}) has been activated.".format(usr_params['groupId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def group_list(self, usr_params={}, groupId=None):
        # GET Group
        '''
        **List the specified CMC GroupInfo**

        You can list the CMC GroupInfo of a specified group using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"

        Or.....

        :param groupId: CMC group ID
        :type groupId: string
        :return: GroupInfo of a CMC group
        :rtype: dict
        :example: group_list(groupId="GROUP-Z")
        '''
        url = self.base_url + "group?"
        method = "GET"
        def_params = {"groupId": "mandatory"}

        if not usr_params and groupId:
            usr_params['groupId'] = groupId

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = {}

        usr_params.clear()
        return msg

    def groups_list(self, usr_params={}):
        # GET Group List
        '''
        **List some of the CMC GroupInfo**

        You can list the CMC GroupInfo of a specified **group** using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :return: GroupInfo of a CMC group
        :rtype: list
        :example: groups_list()
        '''
        url = self.base_url + "group/list"
        method = "GET"
        def_params = {}

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            return json.loads(return_val.text)
        else:
            return False

    def group_ratingplanid_list(self, usr_params={}, groupId=None, region=None):
        # GET Group's Rating Plan ID
        '''
        **List a rating plan ID assigned to a specified CMC group**

        You can list the rating plan ID which are assigned to a specified CMC group using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param groupId: CMC group ID
        :param region: Region name (optional)
        :type groupId: string
        :type region: string
        :return: Rating plan ID
        :rtype: string
        :example: group_ratingplanid_list({"groupId": "GROUP-Z"})
        '''
        url = self.base_url + "group/ratingPlanId?"
        method = "GET"
        def_params = APIParameters.p_group_ratingplan_info
        if not usr_params and groupId:
            usr_params['groupId'] = groupId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = return_val.text
        else:
            msg = ""

        usr_params.clear()
        return msg

    def group_ratingplanid_set(self,
                               usr_params={},
                               groupId=None,
                               ratingPlanId=None,
                               region=None):
        # POST Group's Rating Plan ID
        '''
        **Set a rating plan ID to a specified CMC group**

        You can set the rating plan ID to a specified CMC group using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**groupId**", "**mandatory**"
            "**ratingPlanId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param groupId: CMC group ID
        :param ratingPlanId: Rating plan ID
        :param region: Region name (optional)
        :type groupId: string
        :type ratingPlanId: string
        :type region: string
        :return: Status of the Rating plan ID set operation
        :rtype: string
        :example: group_ratingplanid_set(groupId="GROUP-Z", ratingPlanId="API-TEST-RP")
        '''
        url = self.base_url + "group/ratingPlanId?"
        method = "POST"
        def_params = APIParameters.p_group_ratingplanid_info

        if not usr_params and (groupId and ratingPlanId):
            usr_params['groupId'] = groupId
            usr_params['ratingPlanId'] = ratingPlanId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The rating plan(ID: {0}) was assinged to the group({1}).".format(usr_params['ratingPlanId'], usr_params['groupId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    # Storage Policies
    def storpol_list(self, usr_params={}, policyId=None):
        # GET Storage Policy
        '''
        **List storage policy information specified the Policy ID**

        You can list the detailed information of a storage policy which is specified the policy ID using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**policyId**", "**mandatory**"

        Or.....

        :param policyId: Storage policy ID
        :type policyId: string
        :return: Storage policy information which is specified tht policy ID
        :rtype: dict
        :example: storpol_list({"policyId": "0f7a4ca96ee157b6dc8cba7d1308a7bb"})
        '''
        url = self.base_url + "bppolicy?"
        method = "GET"
        def_params = APIParameters.p_storpol_list

        if not usr_params and policyId:
            usr_params['policyId'] = policyId

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        elif int(return_val.status_code) == 404:
            msg = "The storage policy ID({0}) does not exist.".format(usr_params['policyId'])

        usr_params.clear()
        return msg

    def storpols_list(self, usr_params={}):
        # GET Storage Policy List
        '''
        **List all storage policy information**

        You can list the detailed information of a storage policy which is specified the policy ID using this method.

        .. note::
            There are no mandatory arguments for this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "region", "optional"
            "groupId", "optional"
            "status", "optional"

        Or.....

        :return: All storage policy information
        :rtype: list
        :example: storpols_list()
        '''
        url = self.base_url + "bppolicy/listpolicy"
        method = "GET"
        def_params = APIParameters.p_storpols_list

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            return json.loads(return_val.text)
        else:
            return False

    def storpolid_list(self, usr_params={}, policyName=None):
        '''
        **List a storage policy ID corresponding to a policy name you specified**

        You can list a storage policy ID which is specified by "``Policy Name``" using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**policyName**", "**mandatory**"

        Or.....

        :param policyName: Storage policy name
        :type policyName: string
        :return: Storage policy ID
        :rtype: string
        :example: storpolid_list(policyName="sp-api-test")
        '''
        if usr_params:
            policyName = usr_params['policyName']
        usr_params = {}
        cp_usr_params = copy.deepcopy(usr_params)
        storpols = self.storpols_list(cp_usr_params)

        key_match = False
        for storpol in storpols:
            if storpol['policyName'] == policyName:
                key_match = True
                return storpol['policyId']

        if key_match == False:
            return False

    def storpol_status_change(self,
                              usr_params={},
                              policyName=None,
                              change_to="enable"):
        # DELETE (Disable) Storage Policy
        # POST (Re-Enable) Storage Policy
        '''
        **Change the status of a storage policy**

        You can change the status of a storage policy from enable/disable to disable/enable using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**policyName**", "**mandatory**"
            "change_to", "optional"

        Or.....

        :param policyName: Storage policy name
        :param change_to: Status to be changed from current status (default: ``enable``)
        :type policyName: string
        :type change_to: string
        :return: Status of the storage policy status change operation
        :rtype: string
        :example: storpol_status_change(policyName="sp-api-test", change_to="enable")
        '''
        if usr_params:
            policyName = usr_params['policyName']
        elif not usr_params and policyName:
            usr_params['policyName'] = policyName

        cp_usr_params = copy.deepcopy(usr_params)
        storpol_id = self.storpolid_list(cp_usr_params)
        storpol_status = self.storpol_list({"policyId": storpol_id})['status']

        usr_params.clear()
        usr_params['policyId'] = storpol_id
        if change_to == "enable" and storpol_status != "ACTIVE":
            url = self.base_url + "bppolicy/enable?"
            method = "POST"
            def_params = APIParameters.p_storpol_status_change
            return_val = self.__call_admin_api(url, method, def_params, usr_params)

            storpol_status = self.storpol_list({"policyId": storpol_id})['status']
            msg = 'Storage Policy: {0} status changed --> "{1}"'.format(policyName, storpol_status)
        elif change_to == "disable" and storpol_status != "DISABLED":
            url = self.base_url + "bppolicy/disable?"
            method = "DELETE"
            def_params = APIParameters.p_storpol_status_change
            return_val = self.__call_admin_api(url, method, def_params, usr_params)

            storpol_status = self.storpol_list({"policyId": storpol_id})['status']

        msg = 'Storage Policy: {0} status changed --> "{1}"'.format(policyName, storpol_status)

        usr_params.clear()
        return msg

    def storpol_usage(self, usr_params={}, policyName=None, bucketName=None):
        # GET Storage Policy Usage (Bucket List)
        '''
        **List buckets which are assigned a specified storage policy**

        You can list buckets which are assigned a storage policy you specify using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :param policyName: Storage policy name
        :param bucketName: Bucket name if you want to specify a bucket
        :type policyName: string
        :type bucketName: string
        :return: Bucket names assigned the storage policy you specify
        :rtype: list
        :example: storpol_usage(policyName="2replicas")
        '''
        url = self.base_url + "bppolicy/bucketsperpolicy"
        method = "GET"
        def_params = {}
        sp_usage_info = json.loads(self.__call_admin_api(url, method, def_params, usr_params).text)

        if policyName and not bucketName:
            for row in sp_usage_info:
                if row['policyName'] == policyName:
                    return list(row['buckets'])
                else:
                    continue
            else:
                return False

        elif not policyName and bucketName:
            for row in sp_usage_info:
                if bucketName in row['buckets']:
                    return {"policyName": row['policyName'], "policyId": row['policyId']}
                else:
                    continue
            else:
                return False
        else:
            return sp_usage_info

    # Quality of Service
    def qos_set(self,
                usr_params={},
                qos_level=None,
                userId=None,
                groupId=None,
                storageQuotaKBytes="-1",
                storageQuotaCount="-1",
                wlRequestRate="-1",
                hlRequestRate="-1",
                wlDataKBytesIn="-1",
                hlDataKBytesIn="-1",
                wlDataKBytesOut="-1",
                hlDataKBytesOut="-1",
                region=None):
        # POST QoS Limits
        '''
        **Set QoS to user(s)/group(s)**

        You can set an existing QoS rule to CMC user(s)/group(s) using this method.

        .. warning::
            For the system to actually enforce QoS limits that you have assigned to usersor groups, the QoS feature must be enabled in your system configuration.
            By default it is disabled. To enable it log into the CMC and go toCluster → Cluster Config → Configuration Settings.

        .. note::
            Note that you can enable QoS enforcement just for storage utilization limits, or for storage utilization limits and also request traffic limits.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "**storageQuotaKBytes**", "**mandatory**"
            "**storageQuotaCount**", "**mandatory**"
            "**wlRequestRate**", "**mandatory**"
            "**hlRequestRate**", "**mandatory**"
            "**wlDataKBytesIn**", "**mandatory**"
            "**hlDataKBytesIn**", "**mandatory**"
            "**wlDataKBytesOut**", "**mandatory**"
            "**hlDataKBytesOut**", "**mandatory**"
            "region", "optional"

        Or.....

        :param qos_level: you can specify QoS level as "``user``", "``default-user``", "``default-region-user``", "``group``" and "``default-group``".
        :param userId: CMC user ID
        :param groupId: CMC groupId
        :param storageQuotaKBytes: Storage Size Quota (KB)
        :param storageQuotaCount: Storage Count Quota (Num. of objects)
        :param wlRequestRate: Warning level of number of HTTP requests per minute
        :param hlRequestRate: Maximum allowed number of HTTP requests per minute
        :param wlDataKBytesIn: Warning level for number of uploaded kilobytes per minute
        :param hlDataKBytesIn: Maximum allowed number of uploaded kilobytes per minute
        :param wlDataKBytesOut: Warning level for number of downloaded kilobytes per minute
        :param hlDataKBytesOut: Maximum allowed number of downloaded kilobytes per minute
        :param region: Region name (optional)
        :type qos_level: string
        :type userId: string
        :type groupId: string
        :type storageQuotaKBytes: string
        :type storageQuotaCount: string
        :type wlRequestRate: string
        :type hlRequestRate: string
        :type wlDataKBytesIn: string
        :type hlDataKBytesIn: string
        :type wlDataKBytesOut: string
        :type hlDataKBytesOut: string
        :type region: string
        :return: Status of the QoS limit set operation
        :rtype: string
        :example: qos_set(qos_level="user", userId="gzuser10", groupId="GROUP-Z", storageQuotaKBytes="1024000000000")
        '''
        url = self.base_url + "qos/limits?"
        method = "POST"
        def_params = APIParameters.p_qos_set

        if not usr_params:
            if qos_level == "user":
                # User-level QoS for a specific user (userId=<userId>&groupId=<groupId>)
                usr_params['userId'] = userId
                usr_params['groupId'] = groupId
            elif qos_level == "default-user":
                # Default user-level QoS for a specific group (userId=ALL&groupId=<groupId>)
                usr_params['userId'] = "ALL"
                usr_params['groupId'] = groupId
            elif qos_level == "default-region-user":
                # Default user-level QoS for the whole region (userId=ALL&groupId=*)
                usr_params['userId'] = "ALL"
                usr_params['groupId'] = "*"
            elif qos_level == "group":
                # Group-level QoS for a specific group (userId=*&groupId=<groupId>)
                usr_params['userId'] = "*"
                usr_params['groupId'] = groupId
            elif qos_level == "default-group":
                # Default group-level QoS for the whole region (userId=*&groupId=ALL)
                usr_params['userId'] = "*"
                usr_params['groupId'] = "ALL"
            if region:
                usr_params['region'] = region

        if (not "storageQuotaKBytes" in usr_params) or usr_params['storageQuotaKBytes'] == None:
            usr_params['storageQuotaKBytes'] = storageQuotaKBytes
        if (not "storageQuotaCount" in usr_params) or usr_params['storageQuotaCount'] == None:
            usr_params['storageQuotaCount'] = storageQuotaCount
        if (not "wlRequestRate" in usr_params) or usr_params['wlRequestRate'] == None:
            usr_params['wlRequestRate'] = wlRequestRate
        if (not "hlRequestRate" in usr_params) or usr_params['hlRequestRate'] == None:
            usr_params['hlRequestRate'] = hlRequestRate
        if (not "wlDataKBytesIn" in usr_params) or usr_params['wlDataKBytesIn'] == None:
            usr_params['wlDataKBytesIn'] = wlDataKBytesIn
        if (not "hlDataKBytesIn" in usr_params) or usr_params['hlDataKBytesIn'] == None:
            usr_params['hlDataKBytesIn'] = hlDataKBytesIn
        if (not "wlDataKBytesOut" in usr_params) or usr_params['wlDataKBytesOut'] == None:
            usr_params['wlDataKBytesOut'] = wlDataKBytesOut
        if (not "hlDataKBytesOut" in usr_params) or usr_params['hlDataKBytesOut'] == None:
            usr_params['hlDataKBytesOut'] = hlDataKBytesOut

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The QoS was set to the {0}/{1}.".format(usr_params['groupId'], usr_params['userId'])
        elif int(return_val.status_code) == 503:
            msg = "The QoS feature might not be enabled in your system configuration."
        else:
            msg = ""

        usr_params.clear()
        return msg

    def qos_list(self, usr_params={}, userId=None, groupId=None, region=None):
        # GET QoS Limits
        '''
        **List QoS limits information which is specified**

        You can list QoS limits information which are specified by you using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC group ID
        :param region: Region name (optional)
        :type userId: string
        :type groupId: string
        :type region: string
        :return: Bucket names assigned the storage policy you specify
        :rtype: dict
        :example: qos_list(userId="gzuser10", groupId="GROUP-Z")
        '''
        url = self.base_url + "qos/limits?"
        method = "GET"
        def_params = APIParameters.p_qos_info

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = {}

        usr_params.clear()
        return msg

    def qos_unset(self, usr_params={}, userId=None, groupId=None, region=None):
        # DELETE QoS Limits
        '''
        **Unset QoS to user(s)/group(s)**

        You can unset a QoS rule from CMC user(s)/group(s) using this method.

        .. note::
            The default QoS will be set to the user(s)/group(s) after you unset the specified custom QoS.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**userId**", "**mandatory**"
            "**groupId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC groupId
        :param region: Region name (optional)
        :type userId: string
        :type groupId: string
        :type region: string
        :return: Status of the QoS limit unset operation
        :rtype: string
        :example: qos_unset(userId="gzuser10", groupId="GROUP-Z")
        '''
        url = self.base_url + "qos/limits?"
        method = "DELETE"
        def_params = APIParameters.p_qos_info

        if not usr_params and (userId and groupId):
            usr_params['userId'] = userId
            usr_params['groupId'] = groupId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = "The QoS was unset and the default QoS was assigned to the {0}/{1} automatically.".format(usr_params['groupId'], usr_params['userId'])
        else:
            msg = ""

        usr_params.clear()
        return msg

    def usagereport_list(self,
                         usr_params={},
                         userId=None,
                         groupId=None,
                         operation=None,
                         startTime=None,
                         endTime=None,
                         granularity="raw",
                         reversed=False,
                         limit=100000,
                         pageSize=0,
                         offset=0,
                         region=None,
                         regionOffset=None
                         ):
        # GET Usage Data
        '''
        **List usage report**

        You can list the usage report of the user(s)/group(s) using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**id**", "**mandatory**"
            "**operation**", "**mandatory**"
            "**startTime**", "**mandatory**"
            "**endTime**", "**mandatory**"
            "**granularity**", "**mandatory**"
            "**reversed**", "**mandatory**"
            "limit", "optional"
            "pageSize", "optional"
            "offset", "optional"
            "region", "optional"
            "regionOffset", "optional"

        Or.....

        :param userId: CMC user ID
        :param groupId: CMC groupId
        :param operation: Type of operations (SB/SO/HG/HP/HD)
        :param startTime: Start date of usage report (YYYYMMDDhhmm)
        :param endTime: End date of usage report (YYYYMMDDhhmm)
        :param granularity: raw/hour/day/month (default: ``raw``)
        :param reversed: (default: ``False``)
        :param limit: Maximum number of results to return (default: ``100000``)
        :param pageSize: (default: ``0``)
        :param offset: (default: ``0``)
        :param region: Region name
        :param regionOffset: This argument to specify the region name of your local region
        :type userId: string
        :type groupId: string
        :type operation: string
        :type startTime: string
        :type endTime: string
        :type granularity: string
        :type reversed: bool
        :type limit: string
        :type pageSize: string
        :type offset: string
        :type region: string
        :type regionOffset: string
        :return: Usage report
        :rtype: dict
        :example: usagereport_list(usage_report_params)
        '''
        url = self.base_url + "usage?"
        method = "GET"
        def_params = APIParameters.p_usagereport_info
        now = datetime.datetime.utcnow()

        if usr_params:
            usr_params['id'] = "{0}|{1}".format(usr_params['groupId'], usr_params['userId'])
            del usr_params['groupId']
            del usr_params['userId']
            if not "startTime" in usr_params:
                usr_params['startTime'] = (now - datetime.timedelta(weeks=1)).strftime("%Y%m%d%H%M")
            if not "endTime" in usr_params:
                usr_params['endTime'] = now.strftime("%Y%m%d%H%M")
            if not "granularity" in usr_params:
                usr_params['granularity'] = granularity
            if not "reversed" in usr_params:
                usr_params['reversed'] = "false"

        if not usr_params:
            usr_params['id'] = "{0}|{1}".format(groupId, userId)
            usr_params['operation'] = operation

            if startTime:
                usr_params['startTime'] = startTime
            else:
                usr_params['startTime'] = (now - datetime.timedelta(weeks=1)).strftime("%Y%m%d%H%M")
            if endTime:
                usr_params['endTime'] = endTime
            else:
                usr_params['endTime'] = now.strftime("%Y%m%d%H%M")

            usr_params['granularity'] = granularity
            if reserved == False:
                usr_params['reserved'] = "false"
            elif reserved == True:
                usr_params['reserved'] = "true"

            usr_params['limit'] = limit
            usr_params['pageSize'] = pageSize
            usr_params['offset'] = offset
            if region:
                usr_params['region'] = region
            if regionOffset:
                usr_params['regionOffset'] = regionOffset

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            msg = json.loads(return_val.text)
        else:
            msg = {}

        usr_params.clear()
        return msg

    # System Services
    def license_info(self, usr_params={}):
        # GET License Info
        '''
        **List the license information of your HyperStore system**

        You can list the license information of your HyperStore system using this method.
        The following information will be returned as a Python dictionary.

        .. csv-table:: Return values
            :header: "Key", "Type of Value", "Example"
            :widths: 25, 15, 15

            "License Expiration Date", "string", "2027/05/20 10:46:13"
            "Warning Period", "int", "8"
            "Grace Period", "int", "0"
            "Maximum Net Storage", "int", "-1"

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :return: HyperStore System License Information
        :rtype: dict
        :example: license_info()
        '''
        url = self.base_url + "system/license"
        method = "GET"
        def_params = {}

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            lic_info = json.loads(return_val.text)
            lic_info['expiration'] = (datetime.datetime.fromtimestamp(float(lic_info['expiration'])/1000)).strftime("%Y/%m/%d %H:%M:%S")
            return lic_info
        else:
            return False

    def sys_version(self, usr_params={}):
        # GET System Version
        '''
        **List the version information of your HyperStore system**

        You can list the version information of your HyperStore system using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :return: HyperStore Version Information
        :rtype: string
        :example: sys_version()
        '''
        url = self.base_url + "system/version"
        method = "GET"
        def_params = {}

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            return return_val.text
        else:
            return False

    def node_list(self, usr_params={}, region=None):
        # GET Monitored Node List
        '''
        **List the your HyperStore node ID(s)**

        You can list the your HyperStore node ID(s) using this method.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :param region: Region name (optional)
        :type region: string
        :return: Node ID(s) of your HyperStore system
        :rtype: list
        :example: node_list()
        '''
        method = "GET"
        def_params = {"region": "optional"}
        if region:
            url = self.base_url + "monitor/nodelist?"
        else:
            url = self.base_url + "monitor/nodelist"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            return json.loads(return_val.text)
        else:
            return False

    def node_monitoring_data(self, usr_params={}, nodeId=None, region=None):
        # GET Monitoring Data for Node
        '''
        **List the monitoring data of the HyperStore node you specified**

        You can list the monitoring data of the HyperStore node using this method.

        .. note::
            The return value of this method is very complex and difficult to understand.
            This return value consists of nested Python lists and directories so I recommend that you should arrange this value using Python Programming Laungage.

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            You must set some mandatory keys in the following table into ``usr_params``.

        .. csv-table:: Parameters of usr_params
            :header: "Key", "Mandatory/Optional"
            :widths: 25, 20

            "**nodeId**", "**mandatory**"
            "region", "optional"

        Or.....

        :param nodeId: Node ID of your HyperStore system
        :param region: Region name (optional)
        :type nodeId: string
        :type region: string
        :return: Too much monitoring data
        :rtype: list
        :example: node_monitoring_data(nodeId="cloudian-node1")
        '''
        url = self.base_url + "monitor/host?"
        method = "GET"
        def_params = {"nodeId": "mandatory", "region": "optional"}

        if not usr_params and nodeId:
            usr_params['nodeId'] = nodeId
        if region:
            usr_params['region'] = region

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            monitor_data = json.loads(return_val.text)
            output_data = []
            for metric, data in monitor_data.items():
                if data and isinstance(data, dict) and "timestamp" in data.keys():
                    data['timestamp'] = (datetime.datetime.fromtimestamp(float(data['timestamp'])/1000)).strftime("%Y/%m/%d %H:%M:%S")
                output_data.append({metric: data})
            msg = output_data
        else:
            msg = []

        usr_params.clear()
        return msg

    def region_monitoring_data(self, usr_params={}, region=None):
        # GET Monitoring Data for Region
        '''
        **List the monitoring and perfomance data within the region you specified**

        You can list the monitoring and perfomance data within the region using this method.
        You can see the following data in the return value.

        .. csv-table:: Return values
            :header: "Key", "Description"
            :widths: 25, 50

            "status", "High-level service status for the system as a whole"
            "s3GetTPS", "Across the whole service region, the number of S3 GET transactions processed per second"
            "s3PutTPS", "Across the whole service region, the number of S3 PUT transactions processed per second"
            "s3GetThruput", "Across the whole service region, the data throughput for S3 GET transactions, expressed as MB per second"
            "s3PutThruput", "Across the whole service region, the data throughput for S3 PUT transactions, expressed as MB per second"
            "s3GetLatency", "Across the whole service region, the average latency for completing S3 GET transactions, in milliseconds"
            "s3PutLatency", "Across the whole service region, the average latency for completing S3 PUT transactions, in milliseconds"
            "diskAvailKb", "Across the whole service region, the total mounted disk space remaining still available for Cassandra data directory or HyperStore data directory storage"
            "diskTotalKb", "Across the whole service region, the total size of the disks mounted for Cassandra data directories or HyperStore data directories (the HyperStore File System [HSFS] and erasure coding file system)"
            "nodeStatuses", "List of NodeStatus objects, one for each node in the service region"

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :param region: Region name (optional)
        :type region: string
        :return: Monitoring and perfomance data
        :rtype: list
        :example: region_monitoring_data()
        '''
        method = "GET"
        def_params = {"region": "optional"}
        if region:
            url = self.base_url + "monitor?"
        else:
            url = self.base_url + "monitor"

        return_val = self.__call_admin_api(url, method, def_params, usr_params)
        if int(return_val.status_code) == 200:
            monitor_data = json.loads(return_val.text)
            output_data = []
            for metric, data in monitor_data.items():
                if data and isinstance(data, dict) and "timestamp" in data.keys():
                    data['timestamp'] = (datetime.datetime.fromtimestamp(float(data['timestamp'])/1000)).strftime("%Y/%m/%d %H:%M:%S")
                output_data.append({metric: data})
            return output_data
        else:
            return False

    def hss_info(self, usr_params={}):
        '''
        **List the your HyperStore node ID(s)**

        You can list the your HyperStore node ID(s) using this method.

        .. csv-table:: Return values
            :header: "Key", "Type of Value", "Example"
            :widths: 25, 20, 20

            "version", "string", "6.2 Compiled: 2017-07-26 15:20"
            "nodes", "string", "['cloudian-node1', 'cloudian-node2']"
            "license_expiration", "string", "2027/05/20 10:46:13"

        :param usr_params: Python directory to be set necessary parameters
        :type usr_params: dict

        .. note::
            No needed any parameters in ``usr_params`` for this method.

        :return: Version, node ID(s) and license expiration date of your HyperStore system
        :rtype: OrderedDict
        :example: hss_info()
        '''
        hyperstore = OrderedDict()
        hyperstore['version'] = self.sys_version()
        hyperstore['nodes'] = self.node_list()
        hyperstore['license_expiration'] = self.license_info()['expiration']

        return hyperstore

    def __call_admin_api(self, url, method, def_params, usr_params):
        # Mandatory Keys Check
        mandatory_keys = []
        for key, value in def_params.items():
            if value == 'mandatory':
                mandatory_keys.append(key)
        num_of_mandatory_keys = len(mandatory_keys)

        if num_of_mandatory_keys:
            num_of_key_matches = 0
            for key in usr_params.keys():
                for key_check in mandatory_keys:
                    if key == key_check:
                        num_of_key_matches += 1
            if num_of_key_matches != num_of_mandatory_keys:
                raise ValueError("Missing Required parameters!")

        # Build Query Parameters
        if url[-1] == "?":
            params_list = []
            for usr_key, usr_value in usr_params.items():
                for def_key in def_params.keys():
                    if usr_key == def_key and (usr_value != "" or usr_value != None):
                        params_list.append(usr_key + "=" + usr_value)
            params_str = '&'.join(params_list)
            url = url + params_str

        # Check Admin API parameters users can specify
        if usr_params:
            params_dir = {}
            for usr_key, usr_value in usr_params.items():
                for def_key in def_params.keys():
                    if usr_key == def_key:
                        params_dir[usr_key] = usr_value
            usr_params = params_dir

        if method == "GET":
            response = requests.get(url=url,
                                    headers=self.headers,
                                    verify=False)
        elif method == "POST":
            response = requests.post(url=url,
                                     data=json.dumps(usr_params),
                                     headers=self.headers,
                                     verify=False)
        elif method == "PUT":
            response = requests.put(url=url,
                                    data=json.dumps(usr_params),
                                    headers=self.headers,
                                    verify=False)
        elif method == "DELETE":
            response = requests.delete(url=url,
                                       data=json.dumps(usr_params),
                                       headers=self.headers,
                                       verify=False)

        return response
