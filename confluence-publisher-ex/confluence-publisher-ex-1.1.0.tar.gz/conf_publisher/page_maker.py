import argparse

from . import log, setup_logger
from .auth import parse_authentication
from .confluence_api import create_confluence_api
from .constants import DEFAULT_CONFLUENCE_API_VERSION
from .config import ConfigLoader, ConfigDumper
from .confluence import ConfluencePageManager, Page, Ancestor


def setup_config_overrides(config, url=None):
    if url:
        config.url = url

def main():
    parser = argparse.ArgumentParser(description='Create Confluence pages and update configuration file with it ids')
    parser.add_argument('config', type=str, help='Configuration file')
    parser.add_argument('-u', '--url', type=str, help='Confluence Url')
    auth_group = parser.add_mutually_exclusive_group(required=True)
    auth_group.add_argument('-a', '--auth', type=str, help='Base64 encoded user:password string')
    auth_group.add_argument('-U', '--user', type=str, help='Username (prompt password)')
    parser.add_argument('-pid', '--parent-id', type=str, help='Parent page ID in confluence.')
    parser.add_argument('-v', '--verbose', action='count')

    args = parser.parse_args()
    auth = parse_authentication(args.auth, args.user)
    setup_logger(args.verbose)

    config = ConfigLoader.from_yaml(args.config)
    setup_config_overrides(config, args.url)

    confluence_api = create_confluence_api(DEFAULT_CONFLUENCE_API_VERSION, config.url, auth)
    page_manager = ConfluencePageManager(confluence_api)

    page_manager.make_pages(config, args.parent_id)

    ConfigDumper.to_yaml_file(config, args.config)
    log.info('Config has been updated.')

if __name__ == '__main__':
    main()
