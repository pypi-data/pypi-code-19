from processy import run, ProcResult
from cmdinter import CmdFuncResult, Status


def add_all() -> CmdFuncResult:
    """"""
    title = 'Git Add All.'
    cmd = ['git', 'add', '--all']

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def commit(msg: str) -> CmdFuncResult:
    """"""
    title = 'Git Commit.'
    cmd = ['git', 'commit', '-m', msg]

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def tag(
    version: str,
    branch: str,
    ) -> CmdFuncResult:
    """"""
    title = 'Git Tag.'
    cmd = ['git', 'tag', version, branch]

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def push(branch: str) -> CmdFuncResult:
    """"""
    title = 'Git Push.'
    cmd = ['git', 'push', 'origin', branch, '--tags']

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def get_default_branch() -> CmdFuncResult:
    """"""
    title = 'Get Default Branch.'
    branch = None
    return_code = 0

    cmd1 = ['git', 'show-branch', '--list']
    p1 = run(cmd1, return_stdout=True)

    if p1.out.find('No revs') == -1 and p1.return_code == 0:
        cmd2 = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        p2 = run(cmd2, return_stdout=True)
        branch = p2.out.replace('\n', '')
        return_code = p2.return_code

    status: str = Status.ok if return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=return_code,
        return_msg=status + title,
        return_val=branch,
        )


def status() -> CmdFuncResult:
    """"""
    title = 'Git Status.'
    cmd = ['git', 'status']

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )


def diff() -> CmdFuncResult:
    """"""
    title = 'Git Diff.'
    cmd = ['git', 'diff']

    p: ProcResult = run(cmd)

    status: str = Status.ok if p.return_code == 0 else Status.error

    return CmdFuncResult(
        return_code=p.return_code,
        return_msg=status + title,
        return_val=None
        )
