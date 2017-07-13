def output_links(obj):
    links = []
    for gif in obj['data']:
        links.append(gif['url'])
    return links


def inline_gif(obj):
    return obj['data']['downsized']['url']


def sort_by_max_size(obj, width, height):
    links = []
    for gif in obj['data']['images']:
        if (gif['width'] < width) and (gif['height'] < height):
            links.append(gif['url'])
    return links
