import gzip
import lzma


def __base_parser(lines, count=False):
    for l, line in enumerate(lines, start=1):
        # Skip empty lines
        if len(line) == 0:
            continue

        # Skip comments
        if line.startswith('#') and not line.startswith('#CHROM'):
            continue

        # Parse columns
        if not count:
            line = line.strip().split('\t')

        yield l, line


def __open_file(file, mode="rt"):
    close = False
    fd = file

    # A file path
    if isinstance(file, str):

        # Detect open method
        open_method = open
        if file.endswith('gz') or file.endswith('bgz'):
            open_method = gzip.open
        elif file.endswith('xz'):
            open_method = lzma.open

        fd = open_method(file, mode)
        close = True

    return fd, close


def __count_lines(file):
    fd, close = __open_file(file)
    result = sum(1 for _ in __base_parser(fd, count=True))
    if close:
        fd.close()
    return result