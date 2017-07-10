from typing import List

from stuffer.core import Group, Action

from stuffer import apt


class SpotifyClient(Group):
    def children(self) -> List[Action]:
        return [
            apt.KeyRecv("hkp://keyserver.ubuntu.com:80", "BBEBDCB318AD50EC6865090613B00F1FD2C19886"),
            apt.SourceList("spotify", "deb http://repository.spotify.com stable non-free"),
            apt.Install("spotify-client")
        ]
