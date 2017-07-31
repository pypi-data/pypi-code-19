

from cmd2 import Cmd

from pdcli import router_request


class InteractiveSession(Cmd):
    def __init__(self):
        self.intro = "pd version 0.8"
        self.prompt = "> "

        self.target = None

        Cmd.__init__(self)

#    def __init__(self):
#        #Cmd.__init__(self, use_ipython=False)
#        pass

    def do_target(self, target):
        """
        Set the active target device.
        """
        self.target = target
        self.prompt = "{}> ".format(target)

    def do_chutes(self, arg):
        """
        Print list of chutes.
        """
        url = "http://{}/api/v1/chutes/get".format(self.target)
        router_request("GET", url)

    def do_test(self, arg):
        """
        Test
        """
        self.stdout.write(arg)
        self.stdout.write("hello\n")


if __name__ == "__main__":
    cmd = InteractiveSession()
    cmd.cmdloop()
