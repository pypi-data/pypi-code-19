import prmt
from buildlib.cmds.git import get_default_branch
from cmdinter import run_cmd


def prompt_commit_msg(margin=(0, 1), editor=True) -> str:
    question: str = 'Enter COMMIT message:\n'
    return prmt.string(question, margin=margin, force_val=True, editor=editor)


def prompt_branch(margin=(0, 1)) -> str:
    question: str = 'Enter BRANCH name:\n'
    return prmt.string(question, default=run_cmd(silent=True)(get_default_branch).return_val,
                       margin=margin)
