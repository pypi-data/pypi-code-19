import cli.app
import citrination_client
from citrination.util import determine_url


class App(cli.app.CommandLineApp):

    def main(self):
        """
        Update a Citrination dataset.
        """
        url = determine_url(self.params.host, self.params.project)
        client = citrination_client.CitrinationClient(self.params.api_key, url)

        response = client.update_data_set(self.params.dataset, self.params.name, self.params.description, self.params.share)
        if response.status_code == 200:
            print("Data set has been updated.")
            print(response.content)
        else:
            print("Data set update failed: " + response.reason)

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
        self.add_param("-n", "--name", help="Provide a name for the new dataset.",
                       required=False)
        self.add_param("-D", "--description", help="Provide a description for the dataset.",
                       required=False)
        self.add_param("-s", "--share",
                       help="Share dataset with all users of the site. A value of 1 means the dataset "
                       "will be shared with everyone on the site. A value of 0 means the dataset will only "
                       "be visible by the dataset owner.",
                       required=False, default=None, choices=['0','1'])
        self.add_param("-d", "--dataset", help="Id of the dataset to create a new version for.", required=True,
                       type=int)


if __name__ == "__main__":
    adder = App()
    adder.run()
