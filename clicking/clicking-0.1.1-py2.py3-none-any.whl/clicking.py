from click import echo, style, ClickException


__version__ = '0.1.1'


def info(message, nl=True):
    """Print message in bold white."""
    return echo(message=style(text=message, bold=True), nl=nl)


def progress(message, nl=True):
    """Print message in bold blue."""
    return echo(message=style(text=message, fg='blue', bold=True), nl=nl)


def working(message, nl=True):
    """Print message in bold cyan."""
    return echo(message=style(text=message, fg='cyan', bold=True), nl=nl)


def success(message, nl=True):
    """Print message in bold green."""
    return echo(message=style(text=message, fg='green', bold=True), nl=nl)


def warning(message, nl=True):
    """Print message in bold yellow."""
    return echo(message=style(text=message, fg='yellow', bold=True), nl=nl)


def fail(message, nl=True):
    """Print message in bold red."""
    return echo(message=style(text=message, fg='red', bold=True), nl=nl)


class Error(ClickException):
    """Print an exception in bold red."""
    def show(self, file=None):
        fail('Error: %s' % self.format_message())
