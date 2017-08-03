"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""

import logging
import platform

from twisted.internet import reactor
from twisted.web import server
from twisted.web.http import HTTPChannel

from txhttputil.login_page.LoginElement import LoginElement
from txhttputil.site.AuthCredentials import AllowAllAuthCredentials, AuthCredentials
from txhttputil.site.AuthSessionWrapper import FormBasedAuthSessionWrapper
from txhttputil.site.BasicResource import BasicResource
from txhttputil.site.FileUploadRequest import FileUploadRequest

logger = logging.getLogger(__name__)


def setupSite(name: str,
              rootResource: BasicResource,
              portNum: int = 8000,
              credentialChecker: AuthCredentials = AllowAllAuthCredentials(),
              enableLogin=True):
    ''' Setup Site
    Sets up the web site to listen for connections and serve the site.
    Supports customisation of resources based on user details

    @return: Port object
    '''

    LoginElement.siteName = name

    if enableLogin:
        protectedResource = FormBasedAuthSessionWrapper(rootResource, credentialChecker)
    else:
        logger.critical("Resoruce protection disabled NO LOGIN REQUIRED")
        protectedResource = rootResource

    site = server.Site(protectedResource)
    site.protocol = HTTPChannel
    site.requestFactory = FileUploadRequest

    sitePort = reactor.listenTCP(portNum, site)

    if platform.system() is "Linux":
        import subprocess
        ip = subprocess.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]
    else:
        ip = "0.0.0.0"

    logger.info('%s is alive and listening on http://%s:%s', name, ip, sitePort.port)
    return sitePort
