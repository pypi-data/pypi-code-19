"""Cmdlr yaml access functions."""

import os

import yaml


yaml.Dumper.ignore_aliases = lambda *args: True


def from_file(filepath):
    """Get yaml data from file."""
    with open(filepath, 'r', encoding='utf8') as f:
        return yaml.load(f.read(),
                         Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))


def to_file(filepath, data):
    """Save data to yaml file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w', encoding='utf8') as f:
        content = yaml.dump(data,
                            default_flow_style=False,
                            allow_unicode=True,
                            width=78,
                            indent=4)
        f.write(content)
