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
def main(
        path: str,
        separator: str,
        remove_duplicates: bool,
        remove_non_folders: bool,
        remove_non_abs: bool,
) -> None:
    """
    This script cleans a path, removing elements which repeat or are not valid paths
    :param path:
    :param separator:
    :param remove_duplicates:
    :param remove_non_folders:
    :param remove_non_abs:
    :return:
    """
    path = common.clean(
        path=path,
        separator=separator,
        remove_duplicates=remove_duplicates,
        remove_non_folders=remove_non_folders,
        remove_non_abs=remove_non_abs,
    )
    print(path)


if __name__ == "__main__":
    main()
