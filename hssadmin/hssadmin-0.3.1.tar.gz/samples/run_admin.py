import json
from hssadmin.adminclient import *

base_url = "https://s3-admin.shibuya.local:19443/"
#base_url = "http://admin-tokyo.s3.cloudian.jp:3081/"
enable_auth = True
auth_user = 'sysadmin'
passwd = 'public'

#admin = adminClient(base_url, enable_auth, auth_user, passwd)
admin = adminClient(base_url="https://s3-admin.shibuya.local:19443/",
                    enable_auth=True,
                    user="sysadmin",
                    passwd="public"
                    )

# PUT New User
user_create_params = {
    "userId": "gzuser99",
    "userType": "User",
    "fullName": "Hello HyperStore",
    "emailAddr": "hello@cloudian.com",
    "phone": "XXX-XXXX-XXXX",
    "groupId": "GROUP-Z",
    "website": "http://cloudian.jp",
    "active": True
    }
userpasswd_set_params = {
    "userId": "gzuser15",
    "groupId": "GROUP-Z",
    "password": "P@ssw0rd123"
}
user_delete_params = {
    "userId": "gzuser99",
    "groupId": "GROUP-Z"
}
users_list_params = {
    "groupId": "GROUP-Z",
    "userType": "all",
    "userStatus": "active"
}
user_list_params = {
    "userId": "gzuser1",
    "groupId": "GROUP-Z"
}
user_deactivate_params = {
    "userId": "gzuser13",
    "groupId": "GROUP-Z"
}
s3cred_imp_params = {
    "userId": "gzuser8",
    "groupId": "GROUP-Z",
    "accessKey": "2596b3dd92f86a466c3d",
    "secretKey": "Pmy4HPi9uF5FSlABturX/o6HiB0U5n74Mivy/VFu"
}
rpid_set_params = {
    "userId": "gzuser8",
    "groupId": "GROUP-Z",
    "ratingPlanId": "API-TEST-RP"
}
qos_set_params = {
    "userId": "gzuser5",
    "groupId": "GROUP-Z",
    "storageQuotaKBytes": "500000000000",
    "storageQuotaCount": "-1",
    "wlRequestRate": "10",
    "hlRequestRate": "20",
    "wlDataKBytesIn": "-1",
    "hlDataKBytesIn": "-1",
    "wlDataKBytesOut": "-1",
    "hlDataKBytesOut": "-1"
}
usage_report_params = {
    "userId": "*",
    "groupId": "GROUP-A",
    "operation": "SB",
    "startTime": "201707010000",
    "endTime": "201707302359",
    "granularity": "day"
}
billing_report_params = {
    "userId": "",
    "groupId": "GROUP-A",
    "billingPeriod": "201706"
}

#-------------------------------------#
#----- Test user creation method -----#
#-------------------------------------#
#rtn = admin.user_add(user_create_params)
#print(rtn)

#rtn = admin.user_add(file='data/cmc_user_info.csv')
#print(rtn)

#rtn = admin.userpasswd_set(userpasswd_set_params)

#rtn = admin.userpasswd_set(file='data/cmc_user_info.csv')
#print(rtn)

#-------------------------------------#
#----- Test user deletion method -----#
#-------------------------------------#
#rtn = admin.user_delete(user_delete_params)
#print(rtn)

#rtn = admin.user_delete(file='data/cmc_user_info.csv')
#print(rtn)

#rtn = admin.user_delete(userId="gzuser5", groupId="GROUP-Z", deactive_only=True)
#print(rtn)
#rtn = admin.user_delete(userId="gzuser6", groupId="GROUP-Z", deactive_only=True)
#print(rtn)
#rtn = admin.user_delete(userId="gzuser7", groupId="GROUP-Z", deactive_only=True)
#print(rtn)

#rtn = admin.user_delete(userId="gzuser5", groupId="GROUP-Z", deactive_only=False)
#print(rtn)
#rtn = admin.user_delete(userId="gzuser6", groupId="GROUP-Z", deactive_only=False)
#print(rtn)
#rtn = admin.user_delete(userId="gzuser7", groupId="GROUP-Z", deactive_only=False)
#print(rtn)

#rtn = admin.user_deactivate(userId="gzuser8", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_deactivate(userId="gzuser9", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_deactivate(userId="gzuser10", groupId="GROUP-Z")
#print(rtn)

#rtn = admin.user_delete(file='data/cmc_user_info.csv', deactive_only=True)
#print(rtn)

#rtn = admin.user_delete(file='data/cmc_user_info.csv', deactive_only=False)
#print(rtn)

#-----------------------------------------#
#----- Test user deactivation method -----#
#-----------------------------------------#
#rtn = admin.user_add(file='data/cmc_user_info.csv')
#print(rtn)

#rtn = admin.user_deactivate(user_deactivate_params)
#print(rtn)

#rtn = admin.user_deactivate(userId="gzuser5", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_deactivate(userId="gzuser6", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_deactivate(userId="gzuser7", groupId="GROUP-Z")
#print(rtn)

#---------------------------------------#
#----- Test user activation method -----#
#---------------------------------------#
#rtn = admin.user_activate(user_deactivate_params)
#print(rtn)

#rtn = admin.user_activate(userId="gzuser5", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_activate(userId="gzuser6", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_activate(userId="gzuser7", groupId="GROUP-Z")
#print(rtn)

#----------------------------------#
#----- Test users list method -----#
#----------------------------------#
#rtn = admin.users_list(users_list_params)
#print(rtn)

#rtn = admin.users_list(groupId="GROUP-A", userStatus="inactive")
#print(rtn)
#rtn = admin.users_list(groupId="GROUP-Z", userStatus="inactive")
#print(rtn)
#rtn = admin.users_list(groupId="GROUP-Nothing", userStatus="inactive")
#print(rtn)

#rtn = admin.users_list(groupId="GROUP-A", userStatus="active")
#print(rtn)
#rtn = admin.users_list(groupId="GROUP-Z", userStatus="active")
#print(rtn)
#rtn = admin.users_list(groupId="GROUP-Nothing", userStatus="active")
#print(rtn)

#---------------------------------#
#----- Test user list method -----#
#---------------------------------#
#rtn = admin.user_list(user_list_params)

#rtn = admin.user_list(userId="gzuser1", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_list(userId="gzuser2", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_list(userId="gzuser3", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_list(userId="gzuser100", groupId="GROUP-Z")
#print(rtn)

#-----------------------------------------------#
#----- Test all S3 credentials list method -----#
#-----------------------------------------------#
#rtn = admin.s3credentials_all_list(user_list_params)

#rtn = admin.s3credentials_all_list(userId="gzuser1", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.s3credentials_all_list(userId="gzuser2", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.s3credentials_all_list(userId="gzuser3", groupId="GROUP-Z")
#print(rtn)

#--------------------------------------------------#
#----- Test Active S3 credentials list method -----#
#--------------------------------------------------#
#rtn = admin.s3credentials_active_list(user_list_params)

#rtn = admin.s3credentials_active_list(userId="gzuser1", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.s3credentials_active_list(userId="gzuser2", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.s3credentials_active_list(userId="gzuser3", groupId="GROUP-Z")
#print(rtn)

#--------------------------------------------#
#----- Test S3 credential import method -----#
#--------------------------------------------#
#rtn = admin.s3credential_import(s3cred_imp_params)

#rtn = admin.s3credential_import(userId="gzuser8", groupId="GROUP-Z", accessKey="2596b3dd92f86a466c3d", secretKey="Pmy4HPi9uF5FSlABturX/o6HiB0U5n74Mivy/VFu")
#print(rtn)

#----------------------------------------------#
#----- Test S3 credential creation method -----#
#----------------------------------------------#
#rtn = admin.s3credential_add(userId="gzuser1", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.s3credential_add(userId="gzuser2", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.s3credential_add(userId="gzuser3", groupId="GROUP-Z")
#print(rtn)

#---------------------------------------------#
#----- S3 access key deactivation method -----#
#---------------------------------------------#
#rtn = admin.accesskey_deactivate(accessKey="0c0fa5ad3dd8bd9c08fb")
#print(rtn)
#rtn = admin.accesskey_deactivate(accessKey="00cd1fbf157766fc0647")
#print(rtn)
#rtn = admin.accesskey_deactivate(accessKey="593e67628cb865af9a1d")
#print(rtn)
#rtn = admin.accesskey_deactivate(accessKey="593e67628cb865axxxxx")
#print(rtn)

#-------------------------------------------#
#----- S3 access key activation method -----#
#-------------------------------------------#
#rtn = admin.accesskey_activate(accessKey="0c0fa5ad3dd8bd9c08fb")
#print(rtn)
#rtn = admin.accesskey_activate(accessKey="00cd1fbf157766fc0647")
#print(rtn)
#rtn = admin.accesskey_activate(accessKey="593e67628cb865af9a1d")
#print(rtn)

#-------------------------------------#
#----- S3 secret key list method -----#
#-------------------------------------#
#rtn = admin.secretkey_list({"accessKey": "593e67628cb865af9a1d"})
#print(rtn)
#rtn = admin.secretkey_list(accessKey="0c0fa5ad3dd8bd9c08fb")
#print(rtn)

#----------------------------------------#
#----- User rating plan list method -----#
#----------------------------------------#
#rtn = admin.user_ratingplan_list(userId="gzuser1", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_ratingplan_list(userId="gzuser2", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.user_ratingplan_list(userId="gzuser3", groupId="GROUP-Z")
#print(rtn)

#-------------------------------------------#
#----- User rating plan ID list method -----#
#-------------------------------------------#
rtn = admin.user_ratingplanid_list(userId="gzuser1", groupId="GROUP-Z")
print(rtn)
rtn = admin.user_ratingplanid_list(userId="gzuser2", groupId="GROUP-Z")
print(rtn)
rtn = admin.user_ratingplanid_list(userId="gzuser3", groupId="GROUP-Z")
print(rtn)

#------------------------------------------#
#----- User rating plan ID set method -----#
#------------------------------------------#
#rtn = admin.user_ratingplanid_set(rpid_set_params)

rtn = admin.user_ratingplanid_set(userId="gzuser11", groupId="GROUP-Z", ratingPlanId="API-TEST-RP")
print(rtn)
rtn = admin.user_ratingplanid_set(userId="gzuser12", groupId="GROUP-Z", ratingPlanId="API-TEST-RP")
print(rtn)
rtn = admin.user_ratingplanid_set(userId="gzuser13", groupId="GROUP-Z", ratingPlanId="API-TEST-RP")
print(rtn)

#rtn = admin.group_add(groupId="GROUP-R", groupName="API TEST Group R")
#rtn = admin.group_add(file="cmc_group_info.csv")
#rtn = admin.group_delete(file="cmc_group_info.csv")
#rtn = admin.group_delete(groupId="GROUP-P")
#rtn = admin.group_deactivate({"groupId": "GROUP-Z"})
#rtn = admin.group_activate({"groupId": "GROUP-Z"})

#rtn = admin.group_list(groupId="GROUP-A")
#print(rtn)
#print(rtn)
#rtn = admin.group_list(groupId="GROUP-B")
#rtn = admin.group_list(groupId="GROUP-Z")
#print(rtn)
#rtn = admin.group_list(groupId="GROUP-Nothing")
#print(rtn)

#rtn = admin.groups_list()

#rtn = admin.group_ratingplanid_list({"groupId": "GROUP-A"})
#print(rtn)
#rtn = admin.group_ratingplanid_list({"groupId": "GROUP-B"})
#print(rtn)
#rtn = admin.group_ratingplanid_list({"groupId": "GROUP-Z"})
#print(rtn)
#rtn = admin.group_ratingplanid_list({"groupId": "GROUP-Nothing"})
#print(rtn)

#rtn = admin.group_ratingplanid_list(groupId="GROUP-None")
#rtn = admin.group_ratingplanid_set(groupId="GROUP-Z", ratingPlanId="API-TEST-RP")

#rtn = admin.storpol_list({"policyId": "0f7a4ca96ee157b6dc8cba7d1308a7bb"})
#rtn = admin.storpol_list({"policyId": "0f7a4ca96ee157b6dc8cba7d1308a7bf"})
#rtn = admin.storpols_list()

#rtn = admin.storpolid_list({"policyName": "sp-api-test"})
#rtn = admin.storpolid_list(policyName="sp-api-test")
#rtn = admin.storpolid_list(policyName="nothing")
#rtn = admin.storpol_usage()
#rtn = admin.storpol_usage(bucketName="pythonbucket1")
#rtn = admin.storpol_usage(policyName="2replicas")

#rtn = admin.storpol_status_change({"policyName": "sp-api-test"}, change_to="disable")

#rtn = admin.storpol_status_change(policyName="sp-api-test", change_to="enable")
#print(rtn)
#rtn = admin.storpol_status_change(policyName="sp-api-test", change_to="disable")
#print(rtn)
#rtn = admin.storpol_status_change(policyName="sp-api-test", change_to="enable")
#print(rtn)

#rtn = admin.qos_set(qos_set_params)
#rtn = admin.qos_set(qos_level="user", userId="gzuser10", groupId="GROUP-Z", storageQuotaKBytes="1024000000000")

#rtn = admin.qos_list(userId="gzuser11", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.qos_list(userId="gzuser12", groupId="GROUP-Z")
#rtn = admin.qos_list(userId="gzuser13", groupId="GROUP-Z")
#print(rtn)
#print(rtn)

#rtn = admin.qos_unset({"userId": "gzuser10", "groupId": "GROUP-Z"})

#rtn = admin.qos_unset(userId="gzuser11", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.qos_unset(userId="gzuser12", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.qos_unset(userId="gzuser13", groupId="GROUP-Z")
#print(rtn)
#rtn = admin.qos_unset(userId="gzuser33", groupId="GROUP-Z")
#print(rtn)

#rtn = admin.usagereport_list(usage_report_params)

#rtn = admin.billingreport_list(billing_report_params, output_format="csv", output_file="XXX")

#rtn = admin.license_info()

#rtn = admin.sys_version()
#rtn = admin.node_list()
#rtn = admin.node_list(region="region1")
#rtn = admin.node_monitoring_data(nodeId="cloudian-node1")
#rtn = admin.region_monitoring_data()
#rtn = admin.hss_info()
