import cli.app
import citrination_client
import time
from citrination.util import determine_url
from citrination.util import download_file
from citrination.util import make_directory

class App(cli.app.CommandLineApp):

    def main(self):
        """
        Retrieve the files in a dataset from Citrination.
        """
        url = determine_url(self.params.host, self.params.project)
        client = citrination_client.CitrinationClient(self.params.api_key, url)
        directory_name = 'citrination-files-' + str(time.time()).split(".")[0]        
        if self.params.latest:
            files = client.get_dataset_files(self.params.dataset_id, True)
        else:
            files = client.get_dataset_files(self.params.dataset_id)
        if files and self.params.latest:
            files_arr = files['files']
            if not make_directory(directory_name): return false             
            for file in files_arr:
                download_file(file['url'], file['filename'], directory_name)
        elif files:
            if not make_directory(directory_name): return false
            versions_arr = files['versions']
            for version in versions_arr:
                files_arr = version['files']
                versioned_dir_name = directory_name + "/version_" + str(version['id'])
                make_directory(versioned_dir_name)
                for file in files_arr:
                    download_file(file['url'], file['filename'], versioned_dir_name)

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
        self.add_param("-d", "--dataset_id", help="Id of the dataset to retrieve files from.", required=True, type=int)
        self.add_param("-l", "--latest", help="Boolean flag indicating whether or not to retrieve only the most recent files from the dataset", required=False, action="store_true")

if __name__ == "__main__":
    adder = App()
    adder.run()
