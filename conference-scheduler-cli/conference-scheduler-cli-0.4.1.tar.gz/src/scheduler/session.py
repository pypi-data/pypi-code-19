import sys
from pathlib import Path

this = sys.modules[__name__]

this.folders = {
    'input': Path(Path.cwd(), 'input'),
    'solution': Path(Path.cwd(), 'solution'),
    'build': Path(Path.cwd(), 'build')
}
