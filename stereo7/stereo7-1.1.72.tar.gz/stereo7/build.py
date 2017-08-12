import os
import xml.etree.ElementTree as ET
import fileutils
from project import Project
import build_constants

ConfigurationDebug = 0
ConfigurationRelease = 1
ConfigurationPreRelease = 2


def os_system(cmd, message_on_error=''):
    print 'run:', cmd
    result = os.system(cmd)
    print 'result', result
    if result != 0:
        if message_on_error:
            print message_on_error
        exit(-1)
    return True


def set_values(string, configuration='', scheme=''):
    string = string.replace('@{ROOT}', fileutils.root_dir)
    string = string.replace('@{APPLE_APP_ID}', Project.instance.apple_id)
    string = string.replace('@{APPLE_USER}', Project.instance.apple_auth_user)
    string = string.replace('@{APPLE_PASSWORD}', Project.instance.apple_auth_password)
    string = string.replace('@{APPLE_TEAM_ID}', Project.instance.apple_team_id)
    string = string.replace('@{CONFIGURATION}', configuration)
    string = string.replace('@{SCHEME}', scheme)
    return string


class PlatformWindow:

    def get_configuration_name(self, configuration):
        strs = ['GameDebug', 'Release', 'GameRelease']
        return strs[configuration]

    def set_version(self, packagename, app_version, build_version):
        return True

    def build(self, configuration):
        cmd = set_values(build_constants.win_cmd_build,
                         configuration=self.get_configuration_name(configuration)
                         )
        return os_system(cmd)


class PlatformAndroid:

    def build(self, configuration):
        tasks = ['assembleDebug', 'assembleRelease', 'assembleRelease']
        cmd = set_values(build_constants.android_cmd_build,
                         configuration=tasks[configuration]
                         )
        return os_system(cmd)

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
            exit(-1)


class PlatformIos:

    def build(self, configuration):
        if configuration == ConfigurationDebug or configuration == ConfigurationPreRelease:
            print 'ios build not supported Debug configuration. Use one [release]'
            return False

        scheme = self.arg_parser.scheme
        build = set_values(build_constants.ios_cmd_build, scheme=scheme)
        export_create = set_values(build_constants.ios_export_plist)
        export = set_values(build_constants.ios_cmd_export)
        upload = set_values(build_constants.ios_upload_shell)
        upload_inapps = set_values(build_constants.ios_cmd_upload_inapps)

        if not self.arg_parser.ios_no_build_archive:
            os_system(build)
        else:
            print 'Missing build archive'

        if not self.arg_parser.ios_no_export_ipa:
            os_system(export_create)
            os_system(export)
        else:
            print 'Missing export ipa'

        if self.arg_parser.upload:
            os_system(upload)
            if not self.arg_parser.ios_disable_upload_inapps:
                os_system(upload_inapps)
        else:
            print 'Missing upload build and inapps to iTunesConnect'

        return True

    def set_version(self, packagename, app_version, build_version):
        sh = '/usr/libexec/Plistbuddy'
        plist = '{}/proj.ios/ios/Info.plist'.format(fileutils.root_dir)
        version = '{}.{}'.format(app_version, build_version) if build_version else app_version
        os_system('{} -c "Set CFBundleShortVersionString {}" "{}"'.format(sh, version, plist))
        os_system('{} -c "Set CFBundleIdentifier {}" "{}"'.format(sh, packagename, plist))
        if build_version and str(build_version) != '0':
            os_system('{} -c "Set CFBundleVersion {}" "{}"'.format(sh, build_version, plist))
        return True


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
        print 'Some error'
        exit(-1)
