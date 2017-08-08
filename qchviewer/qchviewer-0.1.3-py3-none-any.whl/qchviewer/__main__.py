#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import tempfile
import os.path
import jinja2


def system(cmd):
    click.echo(cmd)
    os.system(cmd)


@click.command()
@click.argument('qchfile')
def main(**kwargs):
    """
    Console script for qchviewer

    QCHFILE: The qch file path
    """

    if not os.path.isfile(kwargs["qchfile"]):
        raise click.BadParameter(
            "%s not a valid qch file!" % kwargs["qchfile"])

    template = jinja2.Template("""\
<?xml version="1.0" encoding="utf-8" ?>
<QHelpCollectionProject version="1.0">
	<assistant>
		<title>{{ title }}</title>
		<currentFilter>Default</currentFilter>
		<enableAddressBar visible="true">true</enableAddressBar>
	</assistant>
	<docFiles>
		<register>
			<file>{{ path }}</file>
		</register>
	</docFiles>
</QHelpCollectionProject>

""")

    with tempfile.TemporaryDirectory() as temp_dir:
        qhcp_path = os.path.realpath(os.path.join(temp_dir, "main.qhcp"))
        qhcp_content = template.render(
            title=os.path.basename(kwargs["qchfile"]),
            path=os.path.realpath(kwargs["qchfile"]))

        with open(qhcp_path, "wb") as qhcp_file:
            qhcp_file.write(qhcp_content.encode('utf-8'))

        qhc_path = os.path.realpath(os.path.join(temp_dir, "main.qhc"))

        system("qcollectiongenerator \"%s\" -o \"%s\"" % (qhcp_path, qhc_path))

        system("assistant -collectionFile \"%s\"" % qhc_path)


if __name__ == "__main__":
    main()
