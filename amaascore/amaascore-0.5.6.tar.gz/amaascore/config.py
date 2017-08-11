# POTENTIALLY SUPPORT MULTIPLE ENVIRONMENTS
from __future__ import absolute_import, division, print_function, unicode_literals

envs = {'local', 'dev', 'staging', 'production'}

ENVIRONMENT = 'production'
API_VERSION = 'v1.0'

LOCAL_ENDPOINT = 'http://localhost:8000'
NON_PROD_URL = 'https://iwe48ph25i.execute-api.ap-southeast-1.amazonaws.com/%s'
PROD_URL = 'https://api.amaas.com/%s'

ENDPOINTS = {
    'asset_managers': '%s/assetmanager',
    'assets': '%s/asset',
    'books': '%s/book',
    'corporate_actions': '%s/corporateaction',
    'fundamentals': '%s/fundamental',
    'market_data': '%s/marketdata',
    'monitor': '%s/monitor',
    'parties': '%s/party',
    'transactions': '%s/transaction'
}

COGNITO_CLIENT_ID = '55n70ns9u5stie272e1tl7v32v'  # This is not secret - it is just an identifier

# Do not change this
COGNITO_REGION = 'us-west-2'
COGNITO_POOL = 'us-west-2_wKa82vECF'
