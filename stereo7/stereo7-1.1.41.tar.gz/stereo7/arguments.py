

class Parser(object):
    """docstring for Parser"""

    def __init__(self, argv):
        super(Parser, self).__init__()
        self.command = 'help'
        self.args = {}
        self._parse(argv)
        self.root = self.get('-r', '--root', default='.')
        self.platform = self.get('-p', '--platform')
        self.configuration = self.get('-c', '--configuration')
        self.build_version = self.get('--build_version')
        self.upload = self.get('--upload', None, 'y')[0] == 'y'

        self.ios_no_build_archive = self.get('--ios_disable_archive', None, 'n')[0] == 'y'
        self.ios_no_export_ipa = self.get('--ios_disable_export', None, 'n')[0] == 'y'

        if self.command == 'help':
            self.help()
            exit(0)

    def _parse(self, argv):
        if len(argv) > 1:
            self.command = argv[1]
            if self.command in ['-h', '--help']:
                self.command = 'help'
        i = 2
        while i < len(argv):
            arg = argv[i]
            if arg.startswith('-') and i + 1 < len(argv):
                value = argv[i + 1]
                self._add_arg(arg, value)
                i += 2
            else:
                self._add_arg(arg)
                i += 1

    def _add_arg(self, name, value):
        self.args[name] = value

    def get(self, arg, syn=None, default=None):
        if arg in self.args:
            return self.args[arg]
        if syn is not None and syn in self.args:
            return self.args[arg]
        return default if default is not None else ''

    def help(self):
        print ''
        print 'using: $ stereo7 command -r path_to_project [arguments]'
        print ''
        print '  -r (--root) path_to_project (Optional, default is current directory)'
        print ''
        print 'commands:'
        print ''
        print '  help: show help'
        print '    -h: show hiden options'
        print ''
        print '  inapps: build inapps from google spreedsheet'
        print '    no arguments'
        print ''
        print '  build: build and upload (optional)'
        print '    -p, --platform:           platform (ios, android, windows. In future: osx, steam)'
        print '    -c, --configuration:      configuration_name (debug, release. In future: pre-release)'
        print '    --build_version:          version (Optional, number of build version)'
        print '    --upload version:         Optional, use only on ios platform. (y, yes, n, no)'
        print ''
        if self.get('-h', None, 'n')[0] == 'y':
            print ''
            print 'Hiden options'
            print '  build: build and upload (optional)'
            print '    --ios_disable_archive:    disable building archive'
            print '    --ios_disable_export:     disable export archive'
