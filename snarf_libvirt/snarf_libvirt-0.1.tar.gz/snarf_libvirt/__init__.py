from contextlib import contextmanager

import libvirt


class KVMLibvirt:
    def __init__(self, connURL, user):
        self.connURL = connURL
        self.user = user

    @contextmanager
    def openConnection(self):
        """Attempts to open a connection to KVMHost"""
        if self.connURL is None:
            return None

        conn = None
        try:
            connString = 'qemu+ssh://%s@%s/system?socket=/var/run/libvirt/libvirt-sock' % \
                (self.user, self.connURL)
            print('connString : ', connString)
            conn = libvirt.open(connString)

            if conn is not None:
                yield conn
            else:
                yield None
        except libvirt.libvirtError as err:
            print('Libvirt Error: ', err)
            yield None
        finally:
            if conn is not None:
                conn.close()

    def guestHasUpdates(self, guestName, serverDict, conn=None):
        """Check whether or not a guest has updates based off serverDict"""

        state, maxmem, mem, cpus, cput = self.getGuestInfo(guestName, conn)

        if serverDict['memory'] != mem:
            return True

        if serverDict['numCPUs'] != cpus:
            return True

        return False

    def getGuestInfo(self, guestName, conn=None):
        """Get hardware info for a guest """
        if conn is None:
            with self.openConnection() as conn:

                if conn is not None:
                    guest = conn.lookupByName(guestName)

                    if guest is not None:
                        return guest.info()
                    else:
                        return None

        else:
            guest = conn.lookupByName(guestName)

            if guest is not None:
                return guest.info()
            else:
                return None

        return None

    def updateGuest(self, serverDict):
        """Update a single guest's resources based off serverDict"""
        guestName = serverDict['name']
        with self.openConnection() as conn:
            if self.guestHasUpdates(guestName, conn):
                guest = conn.lookupByName(guestName)
                guest.setMemory(serverDict['memory'])
                guest.setVcpus(serverDict['numCPUs'])

        return True
