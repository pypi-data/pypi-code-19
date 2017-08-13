import build_tasks as task

ConfigurationDebug = 0
ConfigurationRelease = 1
ConfigurationPreRelease = 2


class PlatformBuild(object):

    def __init__(self):
        super(PlatformBuild, self).__init__()

    def set_version(self, packagename, app_version, build_version):
        return False

    def build(self, configuration):
        return False

    def upload(self):
        pass

    def upload_inapps(self):
        pass


class PlatformWindow:

    def set_version(self, packagename, app_version, build_version):
        return True

    def build(self, configuration):
        strs = ['GameDebug', 'Release', 'GameRelease']
        return task.windows_build(strs[configuration])


class PlatformAndroid:

    def build(self, configuration):
        gradleTasks = ['assembleDebug', 'assembleRelease', 'assembleRelease']
        return task.android_build(gradleTasks[configuration])

    def set_version(self, packagename, app_version, build_version):
        task.android_change_version(packagename, app_version, build_version)


class PlatformIos:

    def build(self, configuration):
        if configuration == ConfigurationDebug or configuration == ConfigurationPreRelease:
            print 'ios build not supported Debug configuration. Use one [release]'
            return False

        scheme = self.arg_parser.scheme
        task.ios_build_archive(scheme)
        task.ios_export_archive()

        return True

    def set_version(self, packagename, app_version, build_version):
        task.ios_change_version(packagename, app_version, build_version)

    def upload(self):
        task.ios_upload_archive()
        pass

    def upload_inapps(self):
        task.ios_upload_inapps()


def create_builder(arg_parser):
    platform = arg_parser.platform
    platforms = {'windows': PlatformWindow, 'android': PlatformAndroid, 'ios': PlatformIos}
    builder = platforms[platform]()
    builder.arg_parser = arg_parser
    return builder


def run(package_name, app_version, arg_parser):
    configurations = {'debug': ConfigurationDebug, 'release': ConfigurationRelease, 'pre-release': ConfigurationPreRelease, }
    configuration = configurations[arg_parser.configuration]

    builder = create_builder(arg_parser)
    builder.set_version(package_name, app_version, arg_parser.build_version)
    builder.build(configuration)
    if configuration == ConfigurationRelease:
        builder.upload()


def upload(arg_parser):
    builder = create_builder(arg_parser)
    builder.upload()


def upload_inapps(arg_parser):
    builder = create_builder(arg_parser)
    builder.upload_inapps()
