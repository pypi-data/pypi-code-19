from mopidy import commands


class GPIOcontCommand(commands.Command):
    help = 'Some text that will show up in --help'

    def __init__(self):
        super(GPIOcontCommand, self).__init__()
        self.add_argument('--foo')

    def run(self, args, config, extensions):
       # Your command implementation
       return 0