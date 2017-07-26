import os
from distutils.command.install_lib import install_lib
from distutils.core import setup

class g8stor_client_install_lib(install_lib):
    def run(self):
        # run default handler
        install_lib.run(self)

        # locating destination
        target = os.path.join(self.install_dir, 'g8storclient')
        link = "g8storclient.so"

        # detecting system type
        system = "x86_64"
        print("Installing for: %s" % system)

        # creating symlink to the right binary
        current = os.getcwd()
        os.chdir(target)

        if os.path.exists("%s/%s" % (target, link)):
            print("FIXME: File already exists")

        os.symlink("g8storclient-%s.so.py" % system, link)
        os.chdir(current)


setup(
    name = 'g8storclient',
    packages = ['g8storclient'],
    version = '0.1.4',
    description = 'g8os stor native driver',
    author = 'Green IT Globe',
    author_email = 'maxux@greenitglobe.com',
    url = 'https://github.com/jumpscale/g8stor-client-pypi',
    download_url = 'https://github.com/jumpscale/g8stor-client-pypi/tarball/0.1',
    keywords = ['stor', 'gig'],
    classifiers = [],
    cmdclass = {'install_lib': g8stor_client_install_lib}
)
