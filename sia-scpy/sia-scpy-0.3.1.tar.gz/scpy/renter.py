from collections import namedtuple

class SiaRenter(object):
    """
    The renter manages the user's files on the network. The renter's API endpoints expose methods for managing files on the network and managing the renter's allocated funds.
    """
    def __init__(self, scpy):
        self.scpy = scpy

    def __call__(self):
        """
        Returns the current settings along with metrics on the renter's spending.

        :return: Dict with settings
        """
        return self.scpy.get_api('/renter')

    def set_setting(self, parameter, value):
        """
        Modifies settings that control the renter's behavior.

        :param parameter: The parameter to change, e.g: 'renewwindow'
        :type parameter: str
        :param value: The parameter's new value
        :return: True if action succeeded, error message if not
        """
        current_settings = self.scpy.get_api('/renter')['settings']['allowance']
        mod_settings = current_settings[parameter] = value
        return self.scpy.post_api('/renter', data=mod_settings)

    def get_contracts(self):
        """
        Returns active contracts. Expired contracts are not included.

        :return: Array of dicts with contract information
        """
        return self.scpy.get_api('/renter/contracts')['contracts']

    @property
    def downloads(self):
        """
        Lists all files in the download queue.

        :return: Array of dicts with file information and download progress
        """
        return self.scpy.get_api('/renter/downloads')['downloads']

    @property
    def files(self):
        """
        Lists the status of all files.

        :return: Array of dicts with file information
        """
        return self.scpy.get_api('/renter/files')['files']

    @property
    def prices(self):
        """
        Estimated prices of performing various storage and data operations.
        """
        prices = self.scpy.get_api('/renter/prices')
        return namedtuple("Prices", prices.keys())(*[int(x) for x in prices.values()])

    def delete(self, path):
        """
        Deletes a renter file entry. Does not delete any downloads or original files, only the entry in the renter.

        :param path: Location of the file in the renter on the network
        :type path: str
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.post_api(f'/renter/delete/{path}')

    def download(self, path, dest, async=True):
        """
        Downloads a file to the local filesystem.

        :param path: Location of the file in the renter on the network
        :type path: str
        :param dest: Location on disk that the file will be downloaded to
        :type dest: str
        :param async: Whether the call will block until the file has been downloaded
        :type async: bool
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        if async:
            return self.scpy.get_api(f'/renter/downloadasync/{path}', params={'destination': dest})
        else:
            return self.scpy.get_api(f'/renter/download/{path}', params={'destination': dest})

    def rename(self, old, new):
        """
        Renames a file. Does not rename any downloads or source files, only renames the entry in the renter. An error is returned if old path does not exist or new path already exists.

        :param old: Current location of the file in the renter on the network
        :param new: New location of the file in the renter on the network
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.post_api(f'/renter/rename/{old}', data={'newsiapath': new})

    def upload(self, path, source, datapieces, paritypieces):
        """
        Uploads a file to the network from the local filesystem.

        :param path: Location where the file will reside in the renter on the network.
        :param source: Location on disk of the file being uploaded
        :param datapieces: The number of data pieces to use when erasure coding the file
        :param paritypieces: The number of parity pieces to use when erasure coding the file. Total redundancy of the file is ``(datapieces + paritypieces)/datapieces``
        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.post_api(f'/renter/upload/{path}', data={'datapieces': datapieces, 'paritypieces': paritypieces, 'source': source})