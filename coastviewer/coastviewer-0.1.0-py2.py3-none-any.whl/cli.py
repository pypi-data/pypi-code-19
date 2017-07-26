# -*- coding: utf-8 -*-

"""Console script for coastviewer."""

import click
import connexion


def make_app():
    app = connexion.App(__name__, specification_dir='./swagger/')
    title = """
    This is the coastal-viewer api.
    It provides services to acquire data of coasts around the world.
    """
    app.add_api(
        'swagger.yaml',
        arguments={
            'title': title
        }
    )

    @app.route("/")
    def hello():
        return "Hello World!"

    return app

@click.command()
@click.option('--debug', default=False, help='Start application in debugger mode.')
def main(debug, args=None):
    """Console script for coastviewer."""
    app = make_app()
    app.run(debug=debug)


if __name__ == "__main__":
    main()
