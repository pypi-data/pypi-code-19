__author__ = 'xxxx'
import os,sys
import linecache

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
import handleCmd
class ProfileCmd:
    useProfile = 'useProfile'
    delProfile = 'delProfile'
    addProfile = 'addProfile'
    name = 'name'
class ProfileHandler:
    def __init__(self):
        self.handleCmd = handleCmd.handleCmd()

    def getProfileHandlerCmd(self):
        return [ProfileCmd.useProfile, ProfileCmd.addProfile]

    def getProfileHandlerOptions(self):
        return ['--name']

    def useProfileCmd(self, cmd, keyValues):
        if cmd.lower() == ProfileCmd.useProfile.lower():
            if keyValues.has_key(ProfileCmd.name) and len(keyValues[ProfileCmd.name]) > 0:
                _value = keyValues[ProfileCmd.name][0] # use the first value
                if (self.setUserProfile(_value) == True):
                    print "Set user "+_value +" as the default user!"
            else:
                print "Your input is error! Please use cmd \'qcloudcli useprofile --name XX\' to set the default user."
        else:
            print "[", cmd, "] is not right, do you mean "+ProfileCmd.useProfile+" ?"


    def delProfileCmd(self, cmd, keyValues):
        if cmd.lower() == ProfileCmd.delProfile.lower():
            if keyValues.has_key(ProfileCmd.name) and len(keyValues[ProfileCmd.name]) > 0:
                _value = keyValues[ProfileCmd.name][0]
                if (self.delUserProfile(_value) == True):
                    print "Successfully deleted user "+_value +"!"
            else:
                print "Your input is error! Please use cmd \'qcloudcli delprofile --name XX\' to delete user."
        else:
            print "[", cmd, "] is not right, do you mean "+ProfileCmd.delProfile+" ?"

    def addProfileCmd(self, keyValues):
            userKey = ''
            userSecret = ''
            newProfileName = ''
            #check --name is valid
            if keyValues.has_key(ProfileCmd.name) and len(keyValues[ProfileCmd.name]) > 0:
                _value = keyValues[ProfileCmd.name][0] # check the first value
                # only input key and secret
                newProfileName = _value
            else:
                # need input profilename key and value
                newProfileName = raw_input("New profile name: ")
            userKey = raw_input("Qcloud API SecretId: ")
            userSecret = raw_input("Qcloud API SecretKey: ")
            userRegion = raw_input("Region Id(gz,hk,ca,sh,shjr,bj,sg): ")
            userOutput = raw_input("Output Format(json,table,text): ")
            _credentialsPath = os.path.join(self.handleCmd.showQcloudConfigurePath(),self.handleCmd.credentials)
            if os.path.exists(_credentialsPath):
                f = open(_credentialsPath, 'a')
                try:
                    content = "[profile "+newProfileName+"]\nqcloud_secretkey = "+userSecret+"\nqcloud_secretid = " +userKey+ "\n"
                    f.write(content)
                finally:
                    f.close()
            else:
                print "your input is not right, do you want "+ProfileCmd.addProfile+" ?"

            _configurePath =os.path.join(self.handleCmd.showQcloudConfigurePath(),self.handleCmd.configure)
            if os.path.exists(_configurePath):
                f = open(_configurePath, 'a')
                try:
                    content = "[profile " + newProfileName + "]\noutput = " + userOutput + "\nregion = " + userRegion + "\n"
                    f.write(content)
                finally:
                    f.close()
            else:
                print "your input is not right, do you mean "+ProfileCmd.addProfile+" ?"


    def setUserProfile(self,value):
        _configurePath =  os.path.join(self.handleCmd.showQcloudConfigurePath(), self.handleCmd.configure)
        _credentialsPath =  os.path.join(self.handleCmd.showQcloudConfigurePath(),self.handleCmd.credentials)
        useoutput = ''
        useregion = ''
        usekey = ''
        useid = ''
        if os.path.exists(_configurePath):
            va_flag = 0

            f = open(_configurePath, 'r+')
            flist = f.readlines()
            for i in range(len(flist)-2):
                if flist[i].find("profile "+value) > 0:
                    va_flag = 1
                    flist[i] = "[flag]\n"
                    if (not "output" in flist[i+1] or not "region" in flist[i+2]) :
                        print "You have not set uesr \'" + value + "\' output or region!"
                        return False
                    useoutput = flist[i+1]
                    useregion = flist[i+2]
                    break

            if va_flag == 0:
                print "Cannot find user name \'"+ value +"\'!"
                return False

            for j in range(len(flist)-2):
                if flist[j].find("default") > 0:
                    flist[j] = "[profile " + value + "]\n"
                    if "[" in flist[j+1]:
                        flist.insert(j, useoutput)
                        flist.insert(j + 1, useregion)
                        break
                    if "output" in flist[j+1] and not "region" in flist[j+2]:
                        flist.insert(j + 1, useregion)
                    if "region" in flist[j+1] and not "output" in flist[j+2]:
                        flist.insert(j, useoutput)
                    flist[j+1] = useoutput
                    flist[j + 2] = useregion

            for o in range(len(flist) - 2):
                if "flag" in flist[o]:
                    flist[o] = "[default]\n"
                    break

            f = open(_configurePath, 'w+')
            f.writelines(flist)

        if os.path.exists(_credentialsPath):
            key_flag = 0
            id_flag = 0

            f = open(_credentialsPath, 'r+')
            flist = f.readlines()
            for l in range(len(flist)-2):
                if flist[l].find("profile "+value) > 0:
                    key_flag = 1
                    flist[l] = "[flag]\n"
                    if (not "qcloud_secretkey" in flist[l+1] or not "qcloud_secretid" in flist[l+2]):
                        print "You have not set uesr \'" + value + "\' SecretKey or SecretId!"
                        return False
                    usekey = flist[l + 1]
                    useid = flist[l + 2]
                    break

            if key_flag == 0:
                print "Cannot find user name \'" + value + "\'!"
                return False
            for m in range(len(flist)-2):
                if flist[m].find("default") > 0:
                    flist[m] = "[profile " + value + "]\n"
                    if "[" in flist[m + 1]:
                        flist.insert(m, usekey)
                        flist.insert(m + 1, useid)
                        break
                    if "qcloud_secretkey" in flist[m + 1] and not "qcloud_secretid" in flist[m + 2]:
                        flist.insert(m + 1, usekey)
                    if "qcloud_secretid" in flist[m + 1] and not "qcloud_secretkey" in flist[m + 2]:
                        flist.insert(m, useid)
                    flist[m + 1] = usekey
                    flist[m + 2] = useid

            for p in range(len(flist) - 2):
                if "flag" in flist[p]:
                    flist[p] = "[default]\n"
                    break

            f = open(_credentialsPath, 'w+')
            f.writelines(flist)

        return True

    def delUserProfile(self, value):
        _configurePath = os.path.join(self.handleCmd.showQcloudConfigurePath(), self.handleCmd.configure)
        _credentialsPath = os.path.join(self.handleCmd.showQcloudConfigurePath(), self.handleCmd.credentials)
        useoutput = ''
        useregion = ''
        usekey = ''
        useid = ''
        if os.path.exists(_configurePath):
            va_flag = 0
            key_flag = 0
            f = open(_configurePath, 'r+')
            flist = f.readlines()
            for i in range(len(flist) - 2):
                if flist[i].find("profile " + value) > 0:
                    va_flag = 1
                    flist[i] = ""
                    if (not "output" in flist[i + 1] or not "region" in flist[i + 2]):
                       break
                    flist[i + 1] = ""
                    flist[i + 2] = ""
                    break

            if va_flag == 0:
                print "Cannot find user name \'" + value + "\'!"
                return False

            f = open(_configurePath, 'w+')
            f.writelines(flist)

        if os.path.exists(_credentialsPath):

            f = open(_credentialsPath, 'r+')
            flist = f.readlines()
            for l in range(len(flist) - 2):
                if flist[l].find("profile " + value) > 0:
                    key_flag = 1
                    flist[l] = ""
                    if (not "qcloud_secretkey" in flist[l + 1] or not "qcloud_secretid" in flist[l + 2]):
                        break
                    flist[l + 1] = ""
                    flist[l + 2] = ""
                    break

            if key_flag == 0:
                print "Cannot find user name \'" + value + "\'!"
                return False
            f = open(_credentialsPath, 'w+')
            f.writelines(flist)

        return True

if __name__ == "__main__":
    pass