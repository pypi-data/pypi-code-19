import os

import click

from pypathutil import common


@click.command()
@click.option(
    '--separator',
    required=False,
    default=os.pathsep,
    type=str,
    help="what is the path separator",
    show_default=True,
)
@click.option(
    '--remove_duplicates/--no_remove_duplicates',
    required=False,
    default=True,
    help="remove duplicate elements from the path",
    show_default=True,
)
@click.option(
    '--remove_non_folders/--no_remove_non_folders',
    required=False,
    default=True,
    help="remove non folder elements from the path",
    show_default=True,
)
@click.option(
    '--remove_non_abs/--no_remove_non_abs',
    required=False,
    default=True,
    help="remove non absolute folder elements from the path",
    show_default=True,
)
@click.argument(
    'path',
    type=str,
    required=True,
)
@click.argument(
    'folder',
    type=str,
    required=True,
)
def main(
        path: str,
        folder: str,
        separator: str,
        remove_duplicates: bool,
        remove_non_folders: bool,
        remove_non_abs: bool,
) -> None:
    """ remove element from a path """
    new_path = common.remove(
        path=path,
        folder=folder,
        separator=separator,
        remove_duplicates=remove_duplicates,
        remove_non_folders=remove_non_folders,
        remove_non_abs=remove_non_abs,
    )
    print(new_path)

if __name__ == "__main__":
    main()
