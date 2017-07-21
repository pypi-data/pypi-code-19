import os
import re
import requests
import uuid
from BeautifulSoup import BeautifulSoup
from PIL import Image
from tensorpy import classify_image
from tensorpy import constants


def get_image_dimensions(file_name):
    image = Image.open(file_name)
    image_dimensions = image.size  # (width, height) tuple
    return image_dimensions


def convert_to_jpg(file_name):
    infile = file_name
    f, e = os.path.splitext(infile)
    outfile = f + ".jpg"
    if infile != outfile:
        try:
            Image.open(infile).convert('RGBA').save(outfile, "JPEG")
        except IOError:
            raise Exception("Cannot convert %s to jpg!" % file_name)


def _rebuild_source(source, full_base_url):
    source = source.replace('src="//', 'src="http://')
    source = source.replace('src="/', 'src="%s' % full_base_url)
    source = source.replace('src="../', 'src="%s' % full_base_url)
    source = source.replace('src="./', 'src="%s' % full_base_url)
    source = source.replace("src='//", "src='http://")
    source = source.replace("src='/", "src='%s" % full_base_url)
    source = source.replace("src='../", "src='%s" % full_base_url)
    source = source.replace("src='./", "src='%s" % full_base_url)
    return source


def get_all_image_files_on_page(page_url):
    prefix = page_url.split('://')[0]
    simple_url = page_url.split('://')[1]
    base_url = simple_url.split('/')[0]
    full_base_url = prefix + "://" + base_url + "/"
    html = requests.get(page_url)
    completed_source = _rebuild_source(html.text, full_base_url)
    soup = BeautifulSoup(completed_source)
    imgs = soup.fetch('img', src=True)
    image_url_list = []
    for img in imgs:
        link = img["src"].split("src=")[-1]
        if link.endswith('.png') or link.endswith('.jpg'):
            if not link.startswith("http"):
                if ":" not in link:
                    link = full_base_url + link
                else:
                    # The link is weird. Skip it.
                    continue
            image_url_list.append(link)
    return image_url_list


def get_image_classification(image_url):
    downloads_folder = constants.DOWNLOADS_FOLDER
    hex_name = 'temp_image_%s' % uuid.uuid4().get_hex()
    hex_name_png = hex_name + '.png'
    hex_name_jpg = hex_name + '.jpg'

    save_file_as(image_url, hex_name_png)
    convert_to_jpg(
        "%s/%s" % (downloads_folder, hex_name_png))
    os.rename(downloads_folder + "/" + hex_name_png,
              downloads_folder + "/temp_image_png.png")

    best_guess = classify_image.external_run(
            "%s/%s" % (downloads_folder, hex_name_jpg))
    os.rename(downloads_folder + "/" + hex_name_jpg,
              downloads_folder + "/temp_image_jpg.jpg")

    return best_guess.strip()


def is_valid_url(url):
    regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if regex.match(url):
        return True
    else:
        return False


def get_content_type(url):
    content = requests.get(url)
    content_type = content.headers['Content-Type']
    if 'text/html' in content_type:
        return 'html'
    elif 'image/jpeg' in content_type or 'image/png' in content_type:
        return 'image'
    else:
        return 'unsupported'


def _download_file_to(file_url, destination_folder, new_file_name=None):
    if new_file_name:
        file_name = new_file_name
    else:
        file_name = file_url.split('/')[-1]
    r = requests.get(file_url)
    with open(destination_folder + '/' + file_name, "wb") as code:
        code.write(r.content)


def download_file(file_url, destination_folder=None):
    """ Downloads the file from the url to the destination folder.
        If no destination folder is specified, the default one is used. """
    if not destination_folder:
        destination_folder = constants.DOWNLOADS_FOLDER
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
    _download_file_to(file_url, destination_folder)


def save_file_as(file_url, new_file_name, destination_folder=None):
    """ Similar to self.download_file(), except that you get to rename the
        file being downloaded to whatever you want. """
    if not destination_folder:
        destination_folder = constants.DOWNLOADS_FOLDER
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
    _download_file_to(
        file_url, destination_folder, new_file_name)
