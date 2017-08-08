URL = "url"
METHOD = "method"
USER_AGENT = "user_agent"
CLIENT_IP = "client_ip"
X_FORWARDED_FOR = "x_forwarded_for"

STATUS = "status"
CONTENT_LENGTH = "content_length"

XRAY_HEADER = "X-Amzn-Trace-Id"

request_keys = (URL, METHOD, USER_AGENT, CLIENT_IP, X_FORWARDED_FOR)
response_keys = (STATUS, CONTENT_LENGTH)
