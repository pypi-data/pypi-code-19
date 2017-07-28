"""Utility functions

- remove_comments(text)
"""
import re


# Credits to:
# https://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files
# first group captures quoted strings (double or single)
# second group captures comments (//single-line or /* multi-line */)
COMMENT_PATTERN = re.compile("(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)", re.MULTILINE | re.DOTALL)


def remove_comments(text):
    """Remove C and Javascript style comments like // [...] and /* [...] */ from
    the given text.
    """
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return ""  # so we will return empty to remove the comment
        else:  # otherwise, we will return the 1st group
            return match.group(1)  # captured quoted-string

    return COMMENT_PATTERN.sub(_replacer, text)
