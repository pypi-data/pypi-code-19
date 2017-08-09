import traceback as tb
import datetime
import a99

__all__ = ["_LogPart"]

class _LogPart(object):
    """
    This class is a base for XLogDialog and XLogMainWindow
    """
    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # Interface

    def keep_ref(self, obj):
        """Adds obj to internal list to keep a reference to it.

        When using PyQt, it happens that the Python object gets garbage-collected even
        when a C++ Qt object still exists, causing a mess
        """
        self._refs.append(obj)
        return obj


    def add_log_error(self, x, flag_also_show=False):
        """Sets text of labelError."""
        if len(x) == 0:
            x = "(empty error)"
            tb.print_stack()
        x_ = x
        x = '<span style="color: {0!s}">{1!s}</span>'.format(a99.COLOR_ERROR, x)
        self.add_log(x, False)
        if flag_also_show:
            a99.show_error(x_)

    def add_log(self, x, flag_also_show=False):
        """Sets text of labelDescr."""
        if hasattr(self, "label_last_log"):
            self.label_last_log.setText(x)
        if hasattr(self, "textEdit_log"):
            te = self.textEdit_log
            te.append("{0!s} -- {1!s}".format(a99.now_str(), x))
        else:
            a99.get_python_logger().info(x)
        if flag_also_show:
            a99.show_error(x)

    def clear_log(self):
        """Clears text of label_last_log"""
        if hasattr(self, "label_last_log"):
            self.label_last_log.setText("")
