"""dataset command line module."""

import os
import getpass
import datetime

import click
import dtoolcore

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from dtool_cli.cli import dataset_path_argument

README_TEMPLATE = """---
description: Dataset description
project: Project name
confidential: False
personally_identifiable_information: False
owners:
  - name: Your Name
    email: {username}@nbi.ac.uk
    username: {username}
creation_date: {date}
# links:
#  - http://doi.dx.org/your_doi
#  - http://github.com/your_code_repository
# budget_codes:
#  - E.g. CCBS1H10S
""".format(username=getpass.getuser(), date=datetime.date.today())


def create_path(ctx, param, value):
    abspath = os.path.abspath(value)
    if os.path.exists(abspath):
        raise click.BadParameter(
            "File/directory already exists: {}".format(abspath))
    os.mkdir(abspath)
    return abspath


@click.command()
@click.argument("new_dataset_path", callback=create_path)
def create(new_dataset_path):
    """Create an empty dataset."""
    # Create the dataset.
    dataset_name = os.path.basename(new_dataset_path)
    dataset = dtoolcore.DataSet(dataset_name, data_directory="data")
    dataset.persist_to_path(new_dataset_path)

    # Find the abspath of the data directory for user feedback.
    data_path = os.path.join(new_dataset_path, dataset.data_directory)

    # Give the user some feedback and hints on what to do next.
    click.secho("Created dataset ", nl=False, fg="green")
    click.secho(new_dataset_path)
    click.secho("Next steps: ")
    click.secho("1. Add descriptive metadata, e.g: ")
    click.secho(
        "dtool dataset readme interactive {}".format(new_dataset_path),
        fg="cyan")
    click.secho("2. Add raw data, e.g: ")
    click.secho("mv my_data_directory {}/".format(data_path), fg="cyan")
    click.secho("3. Freeze the dataset: ")
    click.secho("dtool dataset freeze {}".format(new_dataset_path), fg="cyan")


@click.group()
def readme():
    """Add descriptive metadata to the readme.
    """


@readme.command()
@dataset_path_argument
def interactive(dataset_path):
    """Update the readme file interactively."""
    dataset = dtoolcore.DataSet.from_path(dataset_path)

    # Create an CommentedMap representation of the yaml readme template.
    yaml = YAML()
    yaml.explicit_start = True
    descriptive_metadata = yaml.load(README_TEMPLATE)

    def prompt_for_values(d):
        """Update the descriptive metadata interactively.

        Uses values entered by the user. Note that the function keeps recursing
        whenever a value is another ``CommentedMap`` or a ``list``. The
        function works as passing dictionaries and lists into a function edits
        the values in place.
        """
        for key, value in d.items():
            if isinstance(value, CommentedMap):
                prompt_for_values(value)
            elif isinstance(value, list):
                for item in value:
                    prompt_for_values(item)
            else:
                new_value = click.prompt(key, type=type(value), default=value)
                d[key] = new_value

    prompt_for_values(descriptive_metadata)

    # Write out the descriptive metadata to the readme file.
    with open(dataset.abs_readme_path, "w") as fh:
        yaml.dump(descriptive_metadata, fh)

    click.secho("Updated readme ", nl=False, fg="green")
    click.secho(dataset.abs_readme_path)
    click.secho("To edit the readme using your default editor:")
    click.secho(
        "dtool dataset readme edit {}".format(dataset._abs_path),
        fg="cyan")


@readme.command()
@dataset_path_argument
def edit(dataset_path):
    """Edit the readme file with your default editor.
    """
    dataset = dtoolcore.DataSet.from_path(dataset_path)
    with open(dataset.abs_readme_path, "r") as fh:
        readme_content = fh.read()
    edited_content = click.edit(readme_content)
    if edited_content is not None:
        with open(dataset.abs_readme_path, "w") as fh:
            fh.write(edited_content)
            click.secho("Updated readme ", nl=False, fg="green")
    else:
        click.secho("Did not update readme ", nl=False, fg="red")
    click.secho(dataset.abs_readme_path)


@readme.command()
@dataset_path_argument
def showpath(dataset_path):
    """Find out where the readme file lives."""
    dataset = dtoolcore.DataSet.from_path(dataset_path)
    click.secho(dataset.abs_readme_path)


@click.command()
@dataset_path_argument
def freeze(dataset_path):
    """Finalise a dataset.

    This step is carried out after all files have been added to the dataset.
    Freezing a dataset finalizes it with a stamp marking it as frozen.
    """
    dataset = dtoolcore.DataSet.from_path(dataset_path)
    dataset.update_manifest()
    # dataset.freeze()
    click.secho("Dataset frozen ", nl=False, fg="green")
    click.secho(dataset._abs_path)
