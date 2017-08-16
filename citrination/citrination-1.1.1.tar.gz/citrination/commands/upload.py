import cli.app
import citrination_client
from citrination.util import determine_url


class App(cli.app.CommandLineApp):

    def main(self):
        """
        Upload a document.
        """
        url = determine_url(self.params.host, self.params.project)
        client = citrination_client.CitrinationClient(self.params.api_key, url)
        message = client.upload_file(self.params.file, self.params.data_set_id)
        if message is not None:
            print message
        else:
            print("Upload failed due to API server being unable to resolve the upload location.")

    def setup(self):
        """
        Setup this application.
        """
        cli.app.CommandLineApp.setup(self)
        self.add_param("-p", "--project", default=None, required=False,
                       help="Name of the project to connect to. This is equal to 'project' in "
                            "https://project.citrination.com. If not set, then a connection will be made to "
                            "https://citrination.com. This setting is superseded by --host if it is set.")
        self.add_param("--host", default=None, required=False,
                       help="Full host to connect, e.g. https://project.citrination.com. This supersedes --project if "
                            "both are set.")
        self.add_param("-k", "--api_key", help="Your API key for the project that you are connecting to.",
                       required=True)
        self.add_param("-f", "--file", help="Path to the file or directory to upload.", required=True)
        self.add_param("-d", "--data_set_id", help="Id of the dataset to upload the file to.", required=True, type=int)

if __name__ == "__main__":
    adder = App()
    adder.run()
