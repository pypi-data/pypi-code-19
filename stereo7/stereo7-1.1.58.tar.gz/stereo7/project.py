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
        data['apple_auth_user'] = ''
        data['apple_auth_password'] = ''
        data['apple_id'] = ''
        data['apple_team_id'] = ''

        path = fileutils.root_dir + '/project.json'
        open(path, 'w').write(json.dumps(data, sort_keys=True, indent=4))
        fileutils.createDir(fileutils.root_dir + '/store')
        fileutils.createDir(fileutils.root_dir + '/store/inapps.itmsp')
        fileutils.write(fileutils.root_dir + '/store/inapps.itmsp/machine-local-data.xml', '<root/>')
        fileutils.write(fileutils.root_dir + '/store/inapps.itmsp/metadata.xml', '<root/>')
        fileutils.write(fileutils.root_dir + '/store/android_inapps.csv',
                        'Product ID,Published State,Purchase Type,Auto Translate,Locale; Title; Description,Auto Fill Prices,Price,Pricing Template ID')

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
        self.apple_auth_user = data['apple_auth_user']
        self.apple_auth_password = data['apple_auth_password']
        self.apple_id = data['apple_id']
        self.apple_team_id = data['apple_team_id']
