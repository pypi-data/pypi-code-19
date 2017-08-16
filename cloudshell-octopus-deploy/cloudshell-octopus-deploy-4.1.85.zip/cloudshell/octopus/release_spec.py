import json


class ReleaseSpec:
    def __init__(self, project_id, version, release_notes='', channel_id=None, selected_packages=None, specific_machine=None):
        self._project_id = project_id
        self._version = version
        self._release_notes = release_notes
        self._channel_id = channel_id
        self._selected_packages = selected_packages
        self._specific_machine = specific_machine

    @property
    def project_id(self):
        return self._project_id

    @property
    def version(self):
        return self._version

    @property
    def release_notes(self):
        return self._release_notes

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def selected_packages(self):
        return self._selected_packages

    @property
    def specific_machine(self):
        return self._specific_machine

    @property
    def json(self):
        release = dict()
        release['ProjectId'] = self.project_id
        release['Version'] = self.version
        release['ReleaseNotes'] = self.release_notes
        if self.channel_id:
            release['ChannelId'] = self.channel_id
        if self.selected_packages:
            release['SelectedPackages'] = self._selected_packages
        if self.specific_machine:
            release['SpecificMachineIds'] = [self._specific_machine]
        return release

    def set_id(self, id):
        self.id = id
