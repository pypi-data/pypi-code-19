"""
easily embed plantuml diagrams in your IPython notebooks
"""

import os
import tempfile
from IPython.core.magic import register_cell_magic
from IPython.display import Image, SVG
import plantuml


@register_cell_magic('plantuml')
def plantuml_cell(_, cell):
    """Generate and display a diagram using Plantuml.
Usage:

%%plantuml figure1

@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml
  """
    plot_file = tempfile.mktemp()
    png_file = plot_file + '.png'
    file(plot_file, 'wb').write(cell)
    plantuml.PlantUML().processes_file(plot_file, png_file)
    return Image(filename=png_file)
