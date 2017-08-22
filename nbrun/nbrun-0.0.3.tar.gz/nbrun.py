import concurrent.futures
import glob
import os
import sys
import time
import traceback

import nbconvert
import nbformat
import click


# The weird retry param is needed because Jupyter kernels
# just randomly dies from time to time (slow clap)
# The issue has been fixed just recently in the following
# pull request and will be part of the next release:
# https://github.com/jupyter/jupyter_client/pull/279
def run_notebook(path, timeout=300, retry=3):
    s = time.time()
    ep = nbconvert.preprocessors.ExecutePreprocessor(
        extra_arguments=["--log-level=40"],
        timeout=timeout,
    )
    path = os.path.abspath(path)
    assert path.endswith('.ipynb')
    nb = nbformat.read(path, as_version=4)
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(path)}})
        return s
    except Exception as e:
        if isinstance(e, RuntimeError) and retry != 0:
            return run_notebook(path, timeout=timeout, retry=retry - 1)
        print("\nException raised while running '{}'\n".format(path))
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)


@click.command()
@click.option('--timeout', default=300, help='Notebook exec timeout')
@click.argument('search_dir', default='.')
def cli(search_dir, timeout):
    path = os.path.abspath(os.path.join(os.getcwd(), search_dir))
    globpattern = os.path.join(path, '**/*.ipynb')

    print('Running notebooks might take a long time...')
    print('===========================================\n')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures_to_path = {}
        for path in glob.iglob(globpattern, recursive=True):
            root, ext = os.path.splitext(os.path.basename(path))
            if root.endswith('_'):
                continue
            futures_to_path[
                executor.submit(run_notebook, path, timeout=timeout)
            ] = path

        for future in concurrent.futures.as_completed(futures_to_path):
            s = future.result()
            sys.stdout.write(
                'Now running ' + os.path.relpath(futures_to_path[future]))
            sys.stdout.flush()
            sys.stdout.write(
                ' -- Finish in {}s\n'.format(int(time.time() - s)))

    print('\n\033[92m'
          '==========================='
          ' Notebook testing done '
          '==========================='
          '\033[0m')
