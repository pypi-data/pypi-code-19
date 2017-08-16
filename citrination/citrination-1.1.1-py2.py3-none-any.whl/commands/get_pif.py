import cli.app
import citrination_client
from citrination.util import determine_url


class App(cli.app.CommandLineApp):

    def main(self):
        """
        Retrieve a PIF from Citrination.
        """
        url = determine_url(self.params.host, self.params.project)
        client = citrination_client.CitrinationClient(self.params.api_key, url)
        if self.params.set_version != None:
            pif = client.get_pif(self.params.dataset_id, self.params.pif_id, self.params.set_version)
        else:
            pif = client.get_pif(self.params.dataset_id, self.params.pif_id)
        print str(pif)

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
        self.add_param("-d", "--dataset_id", help="ID of the dataset to which the PIF belongs.", required=True, type=int)
        self.add_param("-i", "--pif_id", help="The UID for the PIF you are retrieving.", required=True)
        self.add_param("-v", "--set_version", help="The dataset version in which to search for the PIF.", required=False, type=int)

if __name__ == "__main__":
    adder = App()
    adder.run()
