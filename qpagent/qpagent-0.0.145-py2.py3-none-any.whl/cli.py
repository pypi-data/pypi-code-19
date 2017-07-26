#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from multiprocessing import Process

import click

import agent
import agent.config as config
import agent.qualityplatform.agent as qualityplatform_agent
from agent.queue.worker import handle_task
import agent.util.host as host
from server.api import start_server

logger = logging.getLogger(__name__)


def output_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Version: %s" % agent.__version__)
    ctx.exit()


@click.command()
@click.option(
    '-v',
    '--version',
    is_flag=True,
    is_eager=True,
    callback=output_version,
    expose_value=False,
    help="show the version of this tool")
@click.option(
    '-e',
    '--environment',
    default='alpha',
    help='后端接口地址')
def parse_command(environment):
    print(environment)
    config.qualityplatform_api_url = config.qualityplatform_api_url_dict[environment]
    start_agent_client()


def start_agent_client():
    qualityplatform_agent.add_agent(
        host.ip(), config.port, host.name())
    p1 = Process(target=start_server)
    p2 = Process(target=handle_task)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def main():
    print 'A Terminal Tools For agent Agent'
    parse_command()


if __name__ == "__main__":
    main()
