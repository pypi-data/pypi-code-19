from .linkshrink import unshorten as lsh_unshorten


def unshorten(url):
    if 'linkshrink' in url:
        return lsh_unshorten(url)
    else:
        return "Not support site\n"
