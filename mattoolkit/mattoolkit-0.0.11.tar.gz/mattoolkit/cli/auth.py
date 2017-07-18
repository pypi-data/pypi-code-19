from . import cli
from ..api import api as mtk_api


@cli.command()
def login():
    mtk_api.login()

@cli.command()
def logout():
    mtk_api.logout()
