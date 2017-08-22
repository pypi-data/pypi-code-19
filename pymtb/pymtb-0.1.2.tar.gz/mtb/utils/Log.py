import datetime


def log_write_entry(writer, prefix, text, exception=None):
    """
    Prints a message of format: date, time, prefix, text, exception to a writer.

    :param writer:
    :param prefix:
    :param text:
    :param exception:
    """
    now = datetime.now().isoformat(' ')
    header = now + '\t' + prefix + '\t'

    print(header + text, end='\r\n', file=writer)

    if exception is not None:
        print(header + exception, end='\r\n', file=writer)