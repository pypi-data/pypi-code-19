import json

import jwt
import logging
import user_agents
from urllib.parse import urlparse

from flasky.errors import FlaskyTornError, InvalidTokenError

from quark_utilities import errors

logger = logging.getLogger("utilities.security")


class AgentIsNotAuthorized(Exception):

    def __init__(self, status_code=403, message="Agent is not authorized for this action",
                 required_permission=None, required_domain=None,
                 err_code=None, required_membership=None):

        self.status_code = status_code
        self.required_permission = required_permission
        self.required_membership = required_membership
        self.required_domain = required_domain
        self.message = message
        self.err_code = err_code or "errors.notAuthorized"

class Subject(object):

    def __init__(self, token=None, user=None, request=None):
        self.token = token
        self.user = user
        self.request = request

    @property
    def prn(self):
        return self.token.get("prn")

    @property
    def exp(self):
        return self.token.get("exp")

    @property
    def membership_id(self):
        return self._get_data('membership_id')

    def log(self):
        return {
            'ip': self._get_ip(),
            'useragent': self._parse_user_agent(),
            'referer': self._get_referer()
        }

    def _get_data(self, key):
        return self.user.get(key, None) \
            if self.user \
            else self.token.get(key, None)

    def has_permission(self, required_permission):
        return implies_any(
            self.token["roles"], required_permission)

    def has_domain(self, domain_id):
        return domain_id in [domain["_id"] for domain in self.token.get("domains", [])]

    def _get_domain(self, domain_id):
        for domain in self.token["domains"]:
            if domain["domain_id"] == domain_id:
                return domain

    @property
    def is_anonymous(self):
        return True if not self.token else False

    def has_permission_in_root(self, permission):
        return implies_any(self.token["permissions"], permission)

    def has_permission_in_domain(self, domain_id, permission):
        if not self.token:
            return False

        if implies_any(self.token["permissions"], permission):
            return

        domain = self._get_domain(domain_id)
        if not domain or not implies_any(domain.get("permissions", []), permission):
            return False

        return True


    def ensure_permission_in_domain(self, domain_id, permission):
        if not self.is_anonymous and self.has_permission_in_root(permission):
            for domain in self.token["domains"]:
                if str(domain_id) == (domain.get("_id") or domain.get('domain_id')):
                    return True

        elif not self.is_anonymous and self.has_permission_in_domain(domain_id, permission):
            return True

        raise errors.QError(
            err_msg="Subject is not authorized for this action<{}>".format(permission),
            err_code="errors.notAuthorized",
            context={
                "token": self.token
            }
        )

    def has_application(self, app_id):
        return app_id in [app["_id"] for app in self.token.get("applications", [])]

    def _get_referer(self):
        try:
            parsed = urlparse(self.request.headers.get('Referer'))
            return {
                'netloc': parsed.netloc.decode("utf-8"),
                'path': parsed.path.decode("utf-8"),
                'params': parsed.params.decode("utf-8"),
                'query': parsed.query.decode("utf-8"),
                'fragment': parsed.fragment.decode("utf-8")
            }
        except Exception:
            logger.exception("Exception during referer parsing")
            return self.request.headers.get('Referer', None)

    def _get_ip(self):
        try:
            ip = self.request.headers.get("X-Forwarded-For", self.request.remote_ip)
            ip = ip.split(',')[-1].strip(ip)
            return ip
        except Exception:
            logger.exception(msg="Exception during ip parsing")
            return self.request.headers.get("X-Real-Ip")

    def _parse_user_agent(self):
        try:
            return str(user_agents.parse(
                self.request.headers.get('User-Agent')))
        except Exception as ex:
            logging.error(ex)
            return self.request.headers.get('User-Agent')

class SecurityManager(object):

    def __init__(self, app, secret=None, issuer=None):
        self._app = app
        self._secret = secret or app.settings.get('secret', None)
        self._issuer = issuer
        self._app.before_request_funcs.insert(0, self._before_request_hook)
        self._user_loader = None
        self._secret_loader = None

    def user_loader(self, f):
        self._user_loader = f
        return f

    def secret_loader(self, f):
        self._secret_loader = f
        return f

    async def _before_request_hook(self, handler, method_definition):
        required_permission = method_definition.get('secure', None)

        auth_header = handler.request.headers.get('Authorization', None)

        if not auth_header and not required_permission:
            handler.context.subject = Subject(request=handler.request)
            return

        if not auth_header and required_permission:
            raise AgentIsNotAuthorized(
                message="Authorization header is not found")

        if not auth_header.startswith('Bearer'):
            raise AgentIsNotAuthorized(
                message='Unsupported authorization scheme')

        jwt_token = auth_header.split(' ')[1]
        try:
            decoded = jwt.decode(
                jwt_token.strip(),
                key=self._secret,
                verify=True,
                algorithms="HS256",
                leeway=5
            )

            subject = Subject(decoded)
            if self._user_loader:
                logger.info("User loader has been found. Loading user...")
                subject.user = await self._user_loader(handler, method_definition, decoded)

            handler.context.subject = Subject(decoded, request=handler.request)

            if not required_permission:
                return

            user_permissions = decoded.get("permissions", None)
            for user_permission in user_permissions:
                if implies(user_permission, required_permission):
                    logger.info(
                        "User<{}> has permission<{}> to execute this action."
                        .format(decoded["prn"], required_permission))
                    return

            logger.info(
                    "User<username={}, permissions={}> doesn't has "
                    "required permission<{}> to execute this action"
                    .format(
                        decoded["prn"], user_permissions, required_permission))

            raise AgentIsNotAuthorized(message="User has no permission to use this API",
                                       required_permission=required_permission)


        except jwt.exceptions.InvalidTokenError as e:
            raise InvalidTokenError(e.args[0])


_PART_DIVIDER = "."
_SUBPART_DIVIDER = ","
_WILDCARD_TOKEN = "*"


def partify(permission_string):
    """
    @type permission_string: str
    """
    if not permission_string:
        raise ValueError("Wildcard string cannot be none or empty")
    permission_string = permission_string.strip()

    _parts = []

    splitted_parts = permission_string.split(_PART_DIVIDER)
    for splitted_part in splitted_parts:
        subparts = splitted_part.lower().split(_SUBPART_DIVIDER)
        if not subparts:
            raise ValueError(
                    "Wildcard string cannot contains"
                    "parts with only dividers.")
        _parts.append(set(subparts))

    if not _parts:
        raise ValueError("Wildcard string cannot contain only dividers")

    return _parts



def implies(permission_1, permission_2):
    permission_parts = partify(permission_1)
    other_permission_parts = partify(permission_2)

    i = 0
    for other_permission_part in other_permission_parts:
        #: if this permission has less part than other permission,
        #: everything after the number of parts contained
        #: in this permission is implied.
        #: eg: com.admin implies com.admin.read
        if len(permission_parts) - 1 < i:
            return True
        elif _WILDCARD_TOKEN not in permission_parts[i] and \
                not permission_parts[i].issuperset(other_permission_part):
            return False
        i += 1

    for i in range(i, len(permission_parts)-1):
        if _WILDCARD_TOKEN not in permission_parts[i]:
            return False

    return True

def implies_any(permission_collection, permission):
    for _permission in permission_collection:
        if implies(_permission, permission):
            return True

    return False
