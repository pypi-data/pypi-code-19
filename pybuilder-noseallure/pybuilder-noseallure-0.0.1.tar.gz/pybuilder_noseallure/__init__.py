import os.path
import sys
cwd = os.getcwd()
project_main_path = cwd
sys.path.insert(0, project_main_path)

from pybuilder_noseallure.tasks import init_nose  # @UnresolvedImport
from pybuilder_noseallure.tasks import run_unit_tests  # @UnresolvedImport
from pybuilder_noseallure.utils import getImportantDirs  # @UnresolvedImport
from pybuilder_noseallure.utils import prepareArgs  # @UnresolvedImport