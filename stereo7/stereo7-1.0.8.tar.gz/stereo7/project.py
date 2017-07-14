import json
import fileutils
import os


class Project(object):

    instance = None

    def __init__(self, empty=False):
        super(Project, self).__init__()
        if not empty:
            self._parse()

    def create(self):
        data = {}
        data['app_package'] = ''
        data['app_name'] = ''
        data['app_version'] = ''
        data['google_spreedsheet_inapps_id'] = ''
        data['google_api_secret_path'] = ''

        path = fileutils.root_dir + '/project.json'
        open(path, 'w').write(json.dumps(data, sort_keys=True, indent=4))

    def _parse(self):
        path = fileutils.root_dir + '/project.json'
        if not os.path.isfile(path):
            print 'Cannot find project file [project.json]'
            exit(-1)
        data_file = open(path)
        data = json.load(data_file)
        self.package = data['app_package']
        self.name = data['app_name']
        self.version = data['app_version']
        self.gg_inapps = data['google_spreedsheet_inapps_id']
        self.gg_secret_file = fileutils.root_dir + '/' + data['google_api_secret_path']
