import user_agents
import logging
from urllib.parse import urlparse

def create_log(request, **kwargs):
    log = {}

    ip_address = request.headers.get(
        'X-Forwarded-For', request.remote_ip)
    ip_address = ip_address.split(',')[-1].strip()
    ip_address = request.headers.get('X-Real-Ip', ip_address)

    log['useragent'] = kwargs.get('useragent', request.headers.get('User-Agent'))
    log['referer'] = kwargs.get('referer', request.headers.get('Referer'))
    log['ip'] = kwargs.get('ip', ip_address)

    try:
        useragent = str(user_agents.parse(log.get('useragent')))
        log['useragent'] = useragent
    except Exception as ex:
        logging.error(ex)
        pass

    referer = None
    try:
        referer = urlparse(log.get('referer'))
        referer_dict = {
            'netloc': referer.netloc,
            'path': referer.path,
            'params': referer.params,
            'query': referer.query,
            'fragment': referer.fragment
        }
        log['referer'] = referer_dict
    except:
        pass

    return log


