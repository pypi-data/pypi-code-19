from .install import install, add_line, del_line

__version__ = "0.0.4"

help_str = """
=============biubiubiubiu================
This is the *unclebash* package you want!
Version: {}
=========================================

unclebash.install(): install uncle to ~/.bashrc_uncle
unclebash.add_line(): add a bottom line to ~/.bashrc file
unclebash.del_line(): delete the bottom line from ~/.bashrc file

""".format(__version__)
print(help_str)