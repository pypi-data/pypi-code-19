"""
Syntax:

(* group,group,group *)

(* end *)

OR

(* group,group,group *)

(* else *)

(* end *)
"""

import re

from django.contrib.auth.models import AnonymousUser
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class SecretsExtension(Extension):

    def __init__(self, *args, **kwargs):
        
        super(SecretsExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):

        self.md = md

        md.preprocessors.add('secrets',
            SecretsPreprocessor(self.md),
            '_begin',
        )

class SecretsPreprocessor(Preprocessor):

    GROUP_REGEX = r'\w+'
    GROUPS_REGEX = r'(' + GROUP_REGEX + r'(?:,' + GROUP_REGEX + r')*)'
    START_REGEX = '\(\*\s*' + GROUPS_REGEX + '\s*\*\)'

    ELSE_REGEX = r'\(\*\s*else\s*\*\)'
    
    END_REGEX = r'\(\*\s*end\s*\*\)'

    def __init__(self, md, *args, **kwargs):

        super(SecretsPreprocessor, self).__init__(*args, **kwargs)

        self.md = md

    def run(self, lines):

        new_lines = []

        is_hidden = False

        user = getattr(self.md.request, 'user', AnonymousUser())

        for line in lines:
            start_match = re.match(self.START_REGEX, line)
            else_match = re.match(self.ELSE_REGEX, line)
            end_match = re.match(self.END_REGEX, line)

            if else_match:
                is_hidden = not is_hidden
            elif end_match:
                is_hidden = False
            elif is_hidden:
                pass
            elif start_match:
                is_hidden = True
                groups = start_match.group(1).split(',')
                for group in groups:
                    if user.groups.filter(name=group).exists():
                        is_hidden = False
            else:
                new_lines.append(line)

        return new_lines

def makeExtension(*args, **kwargs):
    
    return SecretsExtension(*args, **kwargs)
