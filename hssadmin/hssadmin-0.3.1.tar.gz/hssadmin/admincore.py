class APIParameters():
    '''
    This module defines a number of parameters that are used to judge the mandatory or optional argument for *Cloudian HyperStore(R)* **Admin APIs**.
    
    '''
    p_user_info = {
        "userId": "mandatory",
        "userType": "mandatory",
        "fullName": "optional",
        "emailAddr": "optional",
        "address1": "optional",
        "address2": "optional",
        "city": "optional",
        "state": "optional",
        "zip": "optional",
        "country": "optional",
        "phone": "optional",
        "groupId": "mandatory",
        "website": "optional",
        "active": "optional",
        "canonicalUserId": "optional"
    }
    p_userpasswd_set = {
        "userId": "mandatory",
        "groupId": "mandatory",
        "password": "mandatory"
    }
    p_user_delete = {
        "userId": "mandatory",
        "groupId": "mandatory"
    }
    p_users_list = {
        "groupId": "mandatory",
        "userType": "mandatory",
        "userStatus": "mandatory",
        "prefix": "optional",
        "limit": "optional",
        "offset": "optional"
    }
    p_user_list = {
        "userId": "mandatory",
        "groupId": "mandatory"
    }
    p_storpols_list = {
        "region": "optional",
        "groupId": "optional",
        "status": "optional"
    }
    p_storpol_list = {
        "policyId": "mandatory"
    }
    p_storpol_status_change = {
        "policyId": "mandatory"
    }
    p_s3creds_list = {
        "userId": "mandatory",
        "groupId": "mandatory"
    }
    p_s3cred_imp = {
        "userId": "mandatory",
        "groupId": "mandatory",
        "accessKey": "mandatory",
        "secretKey": "mandatory"
    }
    p_s3cred_add = {
        "userId": "mandatory",
        "groupId": "mandatory"
    }
    p_accesskey_status = {
        "accessKey": "mandatory",
        "isActive": "optional"
    }
    p_secretkey_list = {
        "accessKey": "mandatory"
    }
    p_user_ratingplan_info = {
        "userId": "mandatory",
        "groupId": "mandatory",
        "region": "optional"
    }
    p_user_ratingplanid_info = {
        "userId": "mandatory",
        "groupId": "mandatory",
        "ratingPlanId": "mandatory",
        "region": "optional"
    }
    p_group_info = {
        "groupId": "mandatory",
        "groupName": "optional",
        "ldapGroup": "optional",
        "active": "optional"
    }
    p_group_ratingplan_info = {
        "groupId": "mandatory",
        "region": "optional"
    }
    p_group_ratingplanid_info = {
        "groupId": "mandatory",
        "ratingPlanId": "mandatory",
        "region": "optional"
    }
    p_qos_set = {
        "userId": "mandatory",
        "groupId": "mandatory",
        "storageQuotaKBytes": "mandatory",
        "storageQuotaCount": "mandatory",
        "wlRequestRate": "mandatory",
        "hlRequestRate": "mandatory",
        "wlDataKBytesIn": "mandatory",
        "hlDataKBytesIn": "mandatory",
        "wlDataKBytesOut": "mandatory",
        "hlDataKBytesOut": "mandatory",
        "region": "optional"
    }
    p_qos_info = {
        "userId": "mandatory",
        "groupId": "mandatory",
        "region": "optional"
    }
    p_usagereport_info = {
        "id": "mandatory",
        "operation": "mandatory",
        "startTime": "mandatory",
        "endTime": "mandatory",
        "granularity": "mandatory",
        "reversed": "mandatory",
        "limit": "optional",
        "pageSize": "optional",
        "offset": "optional",
        "region": "optional",
        "regionOffset": "optional"
    }
    p_billingreport_info = {
        "userId": "optional",
        "groupId": "mandatory",
        "billingPeriod": "mandatory"
    }
