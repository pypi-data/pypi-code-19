from django.utils.html import strip_tags


def jsonfeed(items):
    data = [jsonfeed_item(item) for item in items]
    if len(data) == 1:
        data = data[0]
    return data


def jsonfeed_item(item):
    data = {
        'uid': 'urn:uuid:{}'.format(item.uuid),
        'updateDate': item.published_date.strftime('%Y-%m-%dT%X.0Z'),
        'titleText': item.title,
        'mainText': strip_tags(item.text_content),
    }
    if item.audio_content:
        data['streamUrl'] = item.audio_content.url
    if item.display_url:
        data['redirectionURL'] = item.display_url
    return data
