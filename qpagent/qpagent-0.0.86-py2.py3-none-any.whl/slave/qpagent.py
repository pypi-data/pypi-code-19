#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Process
from api.api_server import start_api_server
import agent.api.httpizza as api
from handler.agent_master import handle_task
import agent.util.sys_info as sysInfo
from config import (
    config,
    environment
)
import os
import click
import agent

import logging

APP_DESC = """
     A Terminal Tools For agent Agent
"""

logger = logging.getLogger(__name__)


def output_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version: %s" % agent.__version__)
    ctx.exit()


@click.command()
@click.option('-v', '--version', is_flag=True, is_eager=True, callback=output_version, expose_value=False,
              help="show the version of this tool")
def parse_command():
    config["macaca_dir"] = os.path.join(click.prompt('Please enter a path', default=os.getcwd()))
    config["environment"] = environment[click.prompt('Please enter a environment', default="prod")]
    start_agent_client()


def start_agent_client():
    api.add_agent(sysInfo.get_host_ip(), config["port"], sysInfo.get_host_name())
    p1 = Process(target=start_api_server)
    p2 = Process(target=handle_task)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def main():
    print(APP_DESC)
    parse_command()


if __name__ == "__main__":
    main()
