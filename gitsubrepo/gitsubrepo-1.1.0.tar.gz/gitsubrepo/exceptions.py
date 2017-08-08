from typing import List, Optional


class GitsubrepoException(Exception):
    """
    Base class for all exceptions within this library.
    """


class UnstagedChangeException(GitsubrepoException):
    """
    Raised when there are unexpected unchanged changes to a repository.
    """


class NotAGitRepositoryException(GitsubrepoException):
    """
    Raised when a Git repository was expected but not given.
    """


class NotAGitReferenceException(GitsubrepoException):
    """
    Raised when a Git reference was expected but not given.
    """


class NotAGitSubrepoException(GitsubrepoException):
    """
    Raised when a Git subrepo was expected but not given.
    """


class RunException(GitsubrepoException):
    """
    Raised when a run exited with a non-zero exit code.
    """
    def __init__(self, stdout: str, stderr: str, command: List[str], execution_directory: Optional[str]):
        """
        Constructor.
        :param stdout: what the executable wrote to stdout
        :param stderr: what the executable wrote to stderr
        :param command: the command that was ran
        :param execution_directory: the directory where the command was ran (`None` indicates the current directory)
        """
        self.stdout = stdout
        self.stderr = stderr
        self.command = command
        self.execution_directory = execution_directory

    def __str__(self):
        return f"Command:\n{self.command} ({self.execution_directory})\nstdout:\n{self.stdout}\nstderr:\n{self.stderr}"