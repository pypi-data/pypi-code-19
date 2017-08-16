import cli.app
import citrination_client
from citrination.util import determine_url


class App(cli.app.CommandLineApp):

    def main(self):
        """
        Version a Citrination dataset.
        """
        url = determine_url(self.params.host, self.params.project)
        client = citrination_client.CitrinationClient(self.params.api_key, url)
        response = client.create_data_set_version(self.params.dataset)
        if response.status_code == 200:
            print("Data set version has been created.")
            print response.content
        else:
            print("Data set version creation failed.")

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
        self.add_param("-d", "--dataset", help="Id of the dataset to create a new version for.", required=True,
                       type=int)

if __name__ == "__main__":
    adder = App()
    adder.run()
