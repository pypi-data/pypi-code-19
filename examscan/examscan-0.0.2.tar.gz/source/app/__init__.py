
''' The flipper GUI application. '''

from . import main
from . import inputbox
from . import choicebox
from . import widgets
from . import progress

# Set up shorter names for all of the different classes and some common constructors.
start = main.start
ProgressApp = progress.ProgressApp
SplitButton = widgets.SplitButton
Meter = widgets.Meter
AnimatedCanvas = widgets.AnimatedCanvas

apply_progression = progress.apply_progression
get_input = inputbox.get_input
get_choice = choicebox.get_choice

