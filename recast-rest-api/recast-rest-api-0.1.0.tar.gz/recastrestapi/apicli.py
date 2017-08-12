import click
import os
import subprocess
import logging
log = logging.basicConfig(level = logging.INFO)
def set_config(config):
    if config:
        os.environ['RECASTAPI_CONFIG'] = config
    from apiconfig import config as apiconfig


@click.group()
def apicli():
    pass

@apicli.command()
@click.option('--config', '-c')
def server(config):
    set_config(config)
    from server import app
    port = int(os.environ.get("RECAST_PORT", 5000))
    app.run(host='0.0.0.0', port=port, ssl_context = (os.environ['RECAST_SSL_CERT'],os.environ['RECAST_SSL_KEY']) )

@apicli.command()
@click.option('--config', '-c')
def test(config):
    set_config(config)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
