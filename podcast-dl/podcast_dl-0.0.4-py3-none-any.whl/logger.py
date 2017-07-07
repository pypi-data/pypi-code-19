from .config import Config
import click

class Logger():
  def __init__(self, ui):
    self.logfile = Config.logfile()
    self.verbose = ui.get('verbose')
    self.quiet = ui.get('quiet')
    self.no_logfile = ui.get('no_logfile')

  def error(self, message):
    self.logfile.error(message)
    if not self.quiet:
      color = 'red'
      click.secho(message, fg=color)

  def warning(self, message):
    self.logfile.warning(message)
    if not self.quiet:
      color = 'yellow'
      click.secho(message, fg=color)

  def debug(self, message):
    self.logfile.debug(message)
    if self.verbose and not self.quiet:
      color = 'cyan'
      click.secho(message, fg=color)

  def info(self, message, color='white'):
    self.logfile.info(message)
    if not self.quiet:
      click.secho(message, fg=color)