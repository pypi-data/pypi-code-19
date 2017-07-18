import logging
import user_agents
from urllib.parse import urlparse


class LoggerService(object):

    def create_log_record(self, current_user, data):
        log = {}

        ip_address = current_user.request.headers.get(
            'X-Forwarded-For', current_user.request.remote_ip)
        ip_address = ip_address.split(',')[-1].strip()
        ip_address = current_user.request.headers.get('X-Real-Ip', ip_address)

        log['useragent'] = data.get('useragent', current_user.request.headers.get('User-Agent'))
        log['referer'] = data.get(
            'referer', current_user.request.headers.get('Referer'))
        log['ip'] = data.get('ip', ip_address)

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


