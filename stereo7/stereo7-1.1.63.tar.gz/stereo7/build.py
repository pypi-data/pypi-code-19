import os
import xml.etree.ElementTree as ET
import fileutils
from project import Project


ConfigurationDebug = 0
ConfigurationRelease = 1
ConfigurationPreRelease = 2


class PlatformWindow:

    def get_configuration_name(self, configuration):
        strs = ['GameDebug', 'Release', 'GameRelease']
        return strs[configuration]

    def set_version(self, packagename, app_version, build_version):
        return True

    def build(self, configuration):
        cmd = 'msbuild "{}/../../SyndicateBase/proj.win32/SyndicateBase.sln" /p:Configuration={} /p:Platform=win32 /m'. \
            format(fileutils.root_dir, self.get_configuration_name(configuration))
        result = os.system(cmd)
        print 'Finished with code', result
        return result == 0


class PlatformAndroid:

    def build(self, configuration):
        tasks = ['assembleDebug', 'assembleRelease', 'assembleRelease']
        task = tasks[configuration]
        cmd = 'gradle {} -p {}/proj.android'.format(task, fileutils.root_dir)
        result = os.system(cmd)
        print 'Finished with code', result
        return result == 0

    def set_version(self, packagename, app_version, build_version):
        path = fileutils.root_dir + '/proj.android/app/AndroidManifest.xml'
        ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
        try:
            handle = open(path, 'r')
            tree = ET.parse(handle)
            version = '{}.{}'.format(app_version, build_version) if build_version else app_version
            if build_version and str(build_version) != '0':
                tree.getroot().attrib["{http://schemas.android.com/apk/res/android}versionCode"] = str(build_version)
            tree.getroot().attrib["{http://schemas.android.com/apk/res/android}versionName"] = version
            tree.getroot().attrib["package"] = packagename
            tree.write(path, encoding='utf-8', xml_declaration=True)
            return True
        except:
            print 'cannot open file', path
            return False


class PlatformIos:

    upload_shell = '''
set -ex

# This scripts allows you to upload a binary to the iTunes Connect Store and do it for a specific app_id
# Because when you have multiple apps in status for download, xcodebuild upload will complain that multiple apps are in wait status

# Requires application loader to be installed
# See https://developer.apple.com/library/ios/documentation/LanguagesUtilities/Conceptual/iTunesConnect_Guide/Chapters/SubmittingTheApp.html


IPA_FILE="ipa/Syndicate.ipa"
IPA_FILENAME=$(basename $IPA_FILE)
MD5=$(md5 -q $IPA_FILE)
BYTESIZE=$(stat -f "%z" $IPA_FILE)

TEMPDIR=itsmp
# Remove previous temp
test -d ${TEMPDIR} && rm -rf ${TEMPDIR}
mkdir ${TEMPDIR}
mkdir ${TEMPDIR}/mybundle.itmsp
cp $IPA_FILE ${TEMPDIR}/mybundle.itmsp/$IPA_FILENAME

cat <<EOM > ${TEMPDIR}/mybundle.itmsp/metadata.xml
<?xml version="1.0" encoding="UTF-8"?>
<package version="software4.7" xmlns="http://apple.com/itunes/importer">
<software_assets apple_id="@{APPLE_APP_ID}">
<asset type="bundle">
<data_file>
<file_name>$IPA_FILENAME</file_name>
<checksum type="md5">$MD5</checksum>
<size>$BYTESIZE</size>
</data_file>
</asset>
</software_assets>
</package>
EOM

cp ${IPA_FILE} $TEMPDIR/mybundle.itsmp

USER=@{APPLE_USER}
PASS=@{APPLE_PASSWORD}
/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/itms/bin/iTMSTransporter -m upload -f ${TEMPDIR} -u "$USER" -p "$PASS" -v detailed
'''
    export_plist = '''cat <<EOM > export.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>teamID</key>
        <string>@{APPLE_TEAM_ID}</string>
        <key>method</key>
        <string>app-store</string>
        <key>uploadSymbols</key>
        <true/>
</dict>
</plist>
EOM
'''

    def build(self, configuration):
        if configuration == ConfigurationDebug or configuration == ConfigurationPreRelease:
            print 'ios build not supported Debug configuration. Use one [release]'
            return False
        PlatformIos.upload_shell = PlatformIos.upload_shell.replace('@{APPLE_APP_ID}', Project.instance.apple_id)
        PlatformIos.upload_shell = PlatformIos.upload_shell.replace('@{APPLE_USER}', Project.instance.apple_auth_user)
        PlatformIos.upload_shell = PlatformIos.upload_shell.replace('@{APPLE_PASSWORD}', Project.instance.apple_auth_password)
        PlatformIos.export_plist = PlatformIos.export_plist.replace('@{APPLE_TEAM_ID}', Project.instance.apple_team_id)

        cmd1 = 'xcodebuild -project {}/proj.ios/Syndicate.xcodeproj archive -archivePath Syndicate.xcarchive -scheme Syndicate'.format(fileutils.root_dir)
        cmd2 = 'xcodebuild -exportArchive -archivePath ./Syndicate.xcarchive -exportPath ./ipa -exportOptionsPlist export.plist'
        cmd3 = '/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/itms/bin/iTMSTransporter -m upload -f {}/store/inapps.itmsp -u {} -p {} -v detailed'. \
            format(fileutils.root_dir, Project.instance.apple_auth_user, Project.instance.apple_auth_password)
        result = True

        if not self.arg_parser.ios_no_build_archive:
            result = result and 0 == os.system(cmd1)
        else:
            print 'Missing build archive'

        if not self.arg_parser.ios_no_export_ipa:
            result = result and 0 == os.system(PlatformIos.export_plist)
            result = result and 0 == os.system(cmd2)
        else:
            print 'Missing export ipa'

        if self.arg_parser.upload:
            result = result and 0 == os.system(PlatformIos.upload_shell)
            result = result and 0 == os.system(cmd3)
        else:
            print 'Missing upload build and inapps to iTunesConnect'

        return result

    def set_version(self, packagename, app_version, build_version):
        sh = '/usr/libexec/Plistbuddy'
        plist = '{}/proj.ios/ios/Info.plist'.format(fileutils.root_dir)
        version = '{}.{}'.format(app_version, build_version) if build_version else app_version
        result = True
        result = result and 0 == os.system('{} -c "Set CFBundleShortVersionString {}" "{}"'.format(sh, version, plist))
        result = result and 0 == os.system('{} -c "Set CFBundleIdentifier {}" "{}"'.format(sh, packagename, plist))
        if build_version and str(build_version) != '0':
            result = result and 0 == os.system('{} -c "Set CFBundleVersion {}" "{}"'.format(sh, build_version, plist))
        return result


def run(package_name, app_version, arg_parser):
    configuration = arg_parser.configuration
    platform = arg_parser.platform
    build_version = arg_parser.build_version

    platforms = {'windows': PlatformWindow, 'android': PlatformAndroid, 'ios': PlatformIos}
    configurations = {'debug': ConfigurationDebug, 'release': ConfigurationRelease, 'pre-release': ConfigurationPreRelease, }

    build = platforms[platform]()
    build.arg_parser = arg_parser
    configuration = configurations[configuration]

    result = build.set_version(package_name, app_version, build_version) and \
        build.build(configuration)
    if not result:
        print 'Failed build'
        exit(-1)


if __name__ == '__main__':
    fileutils.root_dir = '/Work/gushchin/td_core/projects/cult'
    run('ios', 'release', 'com.stereo7games.syndicate3', '1.0', '1')
