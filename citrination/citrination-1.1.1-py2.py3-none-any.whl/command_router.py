import cli.app


class CommandRouter(cli.app.CommandLineApp):
    """
    Route commands to applications.
    """
    apps = {}

    def setup(self):
        """
        Setup this router.
        """
        # Only two arguments should be sent to this app: the script name, and
        # the command/help flag. All arguments, save for this script name will
        # be sent to the command.
        if len(self.argv) > 1:
            self.proxied_argv = self.argv[1::]
            self.argv = self.argv[0:2]
        cli.app.CommandLineApp.setup(self)
        self.add_param('command', type=str, help="choose from: upload, create_dataset, update_dataset, create_dataset_version, get_file, get_files, get_pif")

    def main(self):
        """
        Run the application.
        """
        command = self.params.command.lower()
        matched = self.match(command)

        # If an application is matched, run it; else, throw an error.
        if matched:
            app = matched(argv=self.proxied_argv)
            app.run()
        else:
            raise cli.app.Abort("Aborted: command not found: " + self.params.command)

    def match(self, command):
        """
        Iterate through the command registry to find a matching application.
        """
        for app, commands in self.apps.items():
            if command in commands:
                return app
        return False

    def register(self, app, commands):
        """
        Register an application with this router.
        """
        self.apps[app] = commands
