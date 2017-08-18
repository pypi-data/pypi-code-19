import json
import fileutils
import os


class Services:

    def __init__(self):
        self.appodeal_id = ''
        self.flurry_id = ''
        self.facebook_id = ''
        self.gsm_sender_id = ''


class Project(object):

    instance = None

    def __init__(self, arg_parser, empty=False):
        super(Project, self).__init__()
        self.with_pro_version = False
        self.services = None
        self.arg_parser = arg_parser
        if not empty:
            self._parse()

    def create(self):
        data = {}
        data['name'] = ''
        data['app_package'] = ''
        data['app_name'] = ''
        data['app_bundle_name'] = ''
        data['app_version'] = ''
        data['google_spreedsheet_inapps_id'] = ''
        data['google_api_secret_path'] = ''
        data['apple_auth_user'] = ''
        data['apple_auth_password'] = ''
        data['apple_id'] = ''
        data['apple_team_id'] = ''

        # services
        data['services'] = {}
        data['services']['ios'] = {}
        data['services']['android'] = {}
        data['services']['ios']['flurry_id'] = ''
        data['services']['ios']['appodeal_id'] = ''
        data['services']['ios']['facebook_id'] = ''
        data['services']['ios']['gsm_sender_id'] = ''
        data['services']['android']['flurry_id'] = ''
        data['services']['android']['appodeal_id'] = ''
        data['services']['android']['facebook_id'] = ''
        data['services']['android']['gsm_sender_id'] = ''

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
        self.project_name = data['name'] if 'name' in data else None
        self.package = data['app_package']
        self.name = data['app_name']
        self.app_bundle_name = data['app_bundle_name'] if 'app_bundle_name' in data else self.name
        self.version = data['app_version']
        self.gg_inapps = data['google_spreedsheet_inapps_id']
        self.gg_secret_file = fileutils.root_dir + '/' + data['google_api_secret_path']
        self.apple_auth_user = data['apple_auth_user']
        self.apple_auth_password = data['apple_auth_password']
        self.apple_id = data['apple_id']
        self.apple_team_id = data['apple_team_id']
        if self.project_name is None:
            k = self.package.rfind('.')
            self.project_name = self.package[k + 1:]

        if 'services' in data:
            def read(platform):
                js = data['services'][platform]
                if 'lite' in js and 'pro' in js:
                    self.with_pro_version = True
                    self.services[platform]['lite'] = Services()
                    self.services[platform]['lite'].flurry_id = js['lite']['flurry_id']
                    self.services[platform]['lite'].appodeal_id = js['lite']['appodeal_id']
                    self.services[platform]['lite'].facebook_id = js['lite']['facebook_id']
                    self.services[platform]['lite'].gsm_sender_id = js['lite']['gsm_sender_id']
                    self.services[platform]['pro'] = Services()
                    self.services[platform]['pro'].flurry_id = js['pro']['flurry_id']
                    self.services[platform]['pro'].appodeal_id = js['pro']['appodeal_id']
                    self.services[platform]['pro'].facebook_id = js['pro']['facebook_id']
                    self.services[platform]['pro'].gsm_sender_id = js['pro']['gsm_sender_id']
                else:
                    self.with_pro_version = False
                    self.services[platform] = Services()
                    self.services[platform].flurry_id = js['flurry_id']
                    self.services[platform].appodeal_id = js['appodeal_id']
                    self.services[platform].facebook_id = js['facebook_id']
                    self.services[platform].gsm_sender_id = js['gsm_sender_id']

            self.services = {}
            self.services['ios'] = {}
            self.services['android'] = {}
            read('ios')
            read('android')
        if self.with_pro_version and self.arg_parser.app_kind != 'lite':
            self.package += '.' + self.arg_parser.app_kind
