import os
import shutil
from processy import run, ProcResult
from cmdinter import command, CmdResult
from buildlib.yaml import load_yaml, save_yaml
from buildlib.module import load_module_from_file


@command(title='Update Version Num In Config Yaml.')
def update_version_num_in_cfg_yaml(
    config_file: str,
    semver_num: str,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> None:
    """
    Check if version num from proj-cfg is valid.
    Increase version num based on user input or ask user for a new version number.
    """
    cfg: dict = load_yaml(config_file, keep_order=True)
    cfg.update({'version': semver_num})
    save_yaml(cfg, config_file)


@command(title='Push Python Wheel to Gemfury')
def push_python_wheel_to_gemfury(
    wheel_file: str,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    if not os.path.isfile(wheel_file):
        print('Warning: Could not find wheel to push to Gemfury.')
        return_code = 1
    else:
        cmd = ['fury', 'push', wheel_file]
        process: ProcResult = run(cmd, verbose=verbose)
        return_code = process.return_code

    return CmdResult(
        return_code=return_code,
        )


@command(title='Build Python Wheel')
def build_python_wheel(
    clean_dir=False,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """
    Build python wheel for deployment, if it does not exists already.
    @clean_dir: Clean 'build' dir before running build command. This may be necessary because of
    this: https://bitbucket.org/pypa/wheel/issues/147/bdist_wheel-should-start-by-cleaning-up
    """
    build_dir = os.getcwd() + '/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    cmd = ['python', 'setup.py', 'bdist_wheel']
    process: ProcResult = run(cmd, verbose=verbose)

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    return CmdResult(
        return_code=process.return_code,
        )


@command(title='Inject interface.txt into README.md')
def inject_interface_txt_into_readme_md(
    interface_file: str,
    readme_file: str = 'README.md',
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """
    Add content of help.txt into README.md
    Content of help.txt will be placed into the first code block (```) of README.md.
    If no code block is found, a new one will be added to the beginning of README.md.
    """
    readme_content: str = open(readme_file, 'r').read()
    help_content: str = '```\n' + open(interface_file, 'r').read() + '\n```'
    start: int = readme_content.find('```') + 3
    end: int = readme_content.find('```', start)

    if '```' in readme_content:
        mod_content: str = readme_content[0:start - 3] + help_content + readme_content[end + 3:]
    else:
        mod_content: str = help_content + readme_content

    with open('README.md', 'w') as modified_readme:
        modified_readme.write(mod_content)


@command(title='Run Build File')
def run_build_file(
    build_file: str,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    build_module = load_module_from_file(build_file)
    build_module.execute()
    # Add empty lines
    print('\n')


@command(title='Build Read The Docs')
def build_read_the_docs(
    clean_dir: bool = False,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    build_dir = os.getcwd() + '/docs/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    cmd = ['make', 'html']
    run(cmd, cwd=os.getcwd() + '/docs')
