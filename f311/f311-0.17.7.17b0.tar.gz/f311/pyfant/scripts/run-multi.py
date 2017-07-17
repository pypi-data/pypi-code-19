#!/usr/bin/env python
"""
Runs the four Fortran binaries in sequence: `innewmarcs`, `hydro2`, `pfant`, `nulbad`

Check session directory "session-<number>" for log files.
"""

import argparse
import f311.pyfant as pf
import f311.filetypes as ft
import a99
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    # Configuration for Python logging messages.
    logger = a99.get_python_logger()

    # Parser command-line arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    names = pf.Conf().opt.get_names() # option names
    for name in names:
        # name = name.replace('_', '-')
        parser.add_argument("--"+name, type=str, help='')
    args = parser.parse_args()

    # Makes FileOptions object
    oopt = ft.FileOptions()
    for name in names:
        x = args.__getattribute__(name)
        if x is not None:
            oopt.__setattr__(name, x)

    omain = pf.Conf().get_file_main(oopt)




    r = pf.MultiRunnable(self.me.f, self.ae.f, self.oe.f, self.multi_editor.f)
    if self.checkbox_multi_custom_id.isChecked():
        custom_id = self.__get_multi_custom_session_id()
        if _get_custom_dirname(custom_id) == custom_id:
            # Understands that session dirname prefix must be cleared
            r.sid.id_maker.session_prefix_singular = ""
        r.sid.id = self.__get_multi_custom_session_id()
    self._rm.add_runnables([r])

    # c = pf.Combo()
    # c.conf.flag_log_file = True  # Configuration for Fortran messages
    # c.conf.flag_log_console = True  # "
    # c.conf.flag_output_to_dir = False  # Will generate outputs in current directory


    c.run()
    logger.info("Session directory: %s" % c.conf.sid.dir)
