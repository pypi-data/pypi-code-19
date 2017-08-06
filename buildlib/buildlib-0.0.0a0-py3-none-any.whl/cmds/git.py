from processy import run, ProcResult
from cmdinter import command, CmdResult


@command(title='Git Add All')
def add_all(
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    cmd = ['git', 'add', '--all']
    process: ProcResult = run(cmd, verbose=verbose)

    return CmdResult(
        return_code=process.return_code,
        )


@command(title='Git Commit')
def commit(
    msg: str,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    cmd = ['git', 'commit', '-m', msg]
    process: ProcResult = run(cmd, verbose=verbose)

    return CmdResult(
        return_code=process.return_code,
        )


@command(title='Git Tag')
def tag(
    version: str,
    branch: str,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    cmd = ['git', 'tag', version, branch]
    process: ProcResult = run(cmd, verbose=verbose)

    return CmdResult(
        return_code=process.return_code,
        )


@command(title='Git Push')
def push(
    branch: str,
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    cmd = ['git', 'push', 'origin', branch, '--tags']
    process: ProcResult = run(cmd, verbose=verbose)

    return CmdResult(
        return_code=process.return_code,
        )


@command(title='Get Default Branch')
def get_default_branch(
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    branch = None
    return_code = 0

    cmd1 = ['git', 'show-branch', '--list']
    process1 = run(cmd1, verbose=verbose, return_stdout=True)

    if process1.out.find('No revs') == -1 and process1.return_code == 0:
        cmd2 = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        process2 = run(cmd2, return_stdout=True, verbose=verbose)
        branch = process2.out.replace('\n', '')
        return_code = process2.return_code

    return CmdResult(
        return_val=branch,
        return_code=return_code,
        )


@command(title='Git Status')
def status(
    cmd_title=None,
    verbose=None,
    return_stdout=None,
    pretty=None,
    ) -> CmdResult:
    """"""
    cmd = ['git', 'status']
    process: ProcResult = run(cmd, verbose=verbose, return_stdout=return_stdout)

    return CmdResult(
        return_code=process.return_code,
        )
