import cli.app
import citrination_client
import time
from citrination.util import determine_url
from citrination.util import download_file
from citrination.util import make_directory


class App(cli.app.CommandLineApp):

    def main(self):
        """
        Retrieve a file from a dataset from Citrination.
        """
        url = determine_url(self.params.host, self.params.project)
        client = citrination_client.CitrinationClient(self.params.api_key, url)
        if self.params.set_version != None:
            file = client.get_dataset_file(self.params.dataset_id, self.params.file_path, self.params.set_version)
        else:
            file = client.get_dataset_file(self.params.dataset_id, self.params.file_path)
        if file:
            file = file['file']
            directory_name = 'citrination-files-' + str(time.time()).split(".")[0]
            make_directory(directory_name)
            download_file(file['url'], file['filename'], directory_name)

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
        self.add_param("-d", "--dataset_id", help="ID of the dataset to retrieve file from.", required=True, type=int)
        self.add_param("-f", "--file_path", help="Boolean flag indicating whether or not to retrieve only the most recent files from the dataset", required=True)
        self.add_param("-v", "--set_version", help="Dataset version to retrieve file from.", required=False, type=int)

if __name__ == "__main__":
    adder = App()
    adder.run()
