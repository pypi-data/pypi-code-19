import os
import xml.etree.ElementTree as ET
import fileutils


ConfigurationDebug = 0
ConfigurationRelease = 1
ConfigurationPreRelease = 2


class PlatformWindow:

    def get_configuration_name(self, configuration):
        strs = ['GameDebug', 'Release', 'GameRelease']
        return strs[configuration]

    def set_version(self, packagename, app_version, build_version):
        pass

    def build(self, configuration):
        cmd = 'msbuild "{}/../../SyndicateBase/proj.win32/SyndicateBase.sln" /p:Configuration={} /p:Platform=win32 /m'. \
            format(fileutils.root_dir, self.get_configuration_name(configuration))
        result = os.system(cmd)
        print 'Finished with code', result
        return result


class PlatformAndroid:

    def build(self, configuration):
        tasks = ['assembleDebug', 'assembleRelease', 'assembleRelease']
        task = tasks[configuration]
        cmd = 'gradle {} -p {}/proj.android'.format(task, fileutils.root_dir)
        result = os.system(cmd)
        print 'Finished with code', result
        return result

    def set_version(self, packagename, app_version, build_version):
        path = fileutils.root_dir + '/proj.android/app/AndroidManifest.xml'
        ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
        with open(path, 'r') as handle:
            tree = ET.parse(handle)
            if build_version:
                tree.getroot().attrib["{http://schemas.android.com/apk/res/android}versionCode"] = str(build_version)
            tree.getroot().attrib["{http://schemas.android.com/apk/res/android}versionName"] = '{}.{}'.format(app_version, build_version)
            tree.getroot().attrib["package"] = packagename
            tree.write(path, encoding='utf-8', xml_declaration=True)


def run(platform, configuration, package_name, app_version, build_version=None):
    platforms = {'windows': PlatformWindow, 'android': PlatformAndroid, 'ios': PlatformWindow}
    configurations = {'debug': ConfigurationDebug, 'release': ConfigurationRelease, 'pre-release': ConfigurationPreRelease, }

    build = platforms[platform]()
    configuration = configurations[configuration]

    build.set_version(package_name, app_version, build_version)
    build.build(configuration)


if __name__ == '__main__':
    run('android', 'debug', 'com.stereo7games.syndicate3', '1.0', '1')
