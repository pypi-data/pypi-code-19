import urllib2
import os


def determine_url(host, project):
    """
    Determine the URL to use when connecting to a host.

    :param host: Full host name.
    :param project: Project name.
    :return: String with the URL to use.
    """
    host = host if host is None else host.strip()
    if host is not None and len(host) > 0:
        return host
    project = project if project is None else project.strip()
    if project is not None and len(project) > 0:
        return 'https://' + project + '.citrination.com'
    return 'https://citrination.com'

def download_file(url, file_name, target_dir):
    """
    Download a file to a folder.

    :param url: The URL to GET to start the download.
    :param file_name: The desired name of the downloaded file.
    :param target_dir: The target directory to download the file to.
    :return: Nothing
    """

    u = urllib2.urlopen(url)
    f = open('' + target_dir + '/' + file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s To: %s" % (file_name, file_size, target_dir)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

def make_directory(dir_name):
    """
    Creates a directory in the cwd.

    :param dir_name: The name of the directory to make.
    :return: Boolean indicating success or failure of mkdir operation    
    """

    if not os.path.exists(dir_name):
        os.makedirs(dir_name) 
        return True
    else:
        print "Could not make directory to download files"
        return False