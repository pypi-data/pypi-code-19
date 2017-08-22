import os
import shutil
from processy import run, ProcResult
from cmdinter import CmdFuncResult, Status
from buildlib.utils.yaml import save_yaml, load_yaml
from buildlib.utils.module import load_module_from_file


def update_version_num_in_cfg_yaml(
    config_file: str,
    semver_num: str,
    ) -> CmdFuncResult:
    """
    Check if version num from proj-cfg is valid.
    Increase version num based on user input or ask user for a new version number.
    """
    title = 'Update Version Num In Config Yaml.'
    cfg: dict = load_yaml(config_file, keep_order=True)
    cfg.update({'version': semver_num})
    save_yaml(cfg, config_file)

    return CmdFuncResult(
        return_code=0,
        return_msg=Status.ok + title,
        return_val=None
        )


def push_python_wheel_to_gemfury(wheel_file: str) -> CmdFuncResult:
    """"""
    title = 'Push Python Wheel to Gemfury.'
    if not os.path.isfile(wheel_file):
        print('Warning: Could not find wheel to push to Gemfury.')
        return_code = 1
    else:
        cmd = ['fury', 'push', wheel_file]
        p: ProcResult = run(cmd)
        return_code = p.return_code

    status: str = Status.ok if return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=return_code,
        return_msg=status + title,
        return_val=None
        )


def build_python_wheel(clean_dir: bool = False) -> CmdFuncResult:
    """
    Build python wheel for deployment, if it does not exists already.
    @clean_dir: Clean 'build' dir before running build command. This may be necessary because of
    this: https://bitbucket.org/pypa/wheel/issues/147/bdist_wheel-should-start-by-cleaning-up
    """
    title = 'Build Python Wheel.'
    build_dir = os.getcwd() + '/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    cmd = ['python', 'setup.py', 'bdist_wheel']

    p: ProcResult = run(cmd)

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def inject_interface_txt_into_readme_md(
    interface_file: str,
    readme_file: str = 'README.md',
    ) -> CmdFuncResult:
    """
    Add content of help.txt into README.md
    Content of help.txt will be placed into the first code block (```) of README.md.
    If no code block is found, a new one will be added to the beginning of README.md.
    """
    title = 'Inject interface.txt into README.md.'
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

    return CmdFuncResult(
        return_code=0,
        return_msg=Status.ok + title,
        return_val=None
        )


def run_build_file(build_file: str) -> CmdFuncResult:
    """"""
    title = 'Run Build File.'
    build_module = load_module_from_file(build_file)
    build_module.execute()

    # Add empty lines
    print('\n')

    return CmdFuncResult(
        return_code=0,
        return_msg=Status.ok + title,
        return_val=None
        )


def build_read_the_docs(clean_dir: bool = False) -> CmdFuncResult:
    """"""
    title = 'Build Read The Docs.'
    build_dir = os.getcwd() + '/docs/build'

    if clean_dir and os.path.isdir(build_dir):
        shutil.rmtree(build_dir)

    cmd = ['make', 'html']
    p: ProcResult = run(cmd, cwd=os.getcwd() + '/docs')

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def create_py_venv(
    py_bin: str,
    venv_dir: str,
    ) -> CmdFuncResult:
    """
    @interpreter: must be the exact interpreter name. E.g. 'python3.5'
    """
    title = 'Create Python Virtual Environment.'
    cmd: list = [py_bin + ' -m venv ' + venv_dir]

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def create_autoenv(
    venv_dir: str,
    ) -> CmdFuncResult:
    """
    Create autoenv for automatic activation of virtual env when cd into dir.
    """
    title = 'Create Auto Env File.'
    env_file_path: str = os.path.normpath(venv_dir) + '/' + '.env'
    venv_dir_base = os.path.basename(os.path.normpath(venv_dir))

    with open(env_file_path, 'w+') as f:
        f.write('source ' + venv_dir_base + '/bin/activate\n')

    return CmdFuncResult(
        return_code=0,
        return_msg=Status.ok + title,
        return_val=None
        )
