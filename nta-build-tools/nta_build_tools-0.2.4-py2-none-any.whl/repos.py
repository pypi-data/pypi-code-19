# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2017, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""Info about the repos that this package manages."""

import os

# List of managed repos in order of installation
DEFAULT_REPOS = ["nupic.core", "nupic", "htmresearch-core", "htmresearch"]

# List of managed repos with C++ builds
DEFAULT_REPOS_CPP = ["nupic.core", "htmresearch-core"]

# Mapping from repo name to Python package name
PACKAGE_NAMES = {
  "nupic.core": "nupic.bindings",
  "nupic": "nupic",
  "htmresearch-core": "htmresearch-core",
  "htmresearch": "htmresearch",
}

# Mapping from repo name to Python import package used to test installation
IMPORT_TEST = {
  "nupic.core": ("nupic.bindings",),
  # "nupic" is not sufficient since it doesn't distinguish from nupic.bindings
  "nupic": ("nupic.algorithms",),
  "htmresearch-core": ("htmresearch_core", "nupic.research.core"),
  "htmresearch": ("htmresearch",),
}

# Python source path for repos. These are written to easy-install.pth during
# developer installs.
SRC_PATH = {
  "nupic.core": (
      os.path.expanduser("~/nta/nupic.core/bindings/py/src"),
      os.path.expanduser("~/nta/nupic.core/bindings/py"),
  ),
  "nupic": (
      os.path.expanduser("~/nta/nupic/src"),
  ),
  "htmresearch-core": (
      os.path.expanduser("~/nta/htmresearch-core/bindings/py/src"),
      os.path.expanduser("~/nta/htmresearch-core/bindings/py"),
      os.path.expanduser("~/nta/nupic.research.core/bindings/py"),
  ),
  "htmresearch": (
      os.path.expanduser("~/nta/htmresearch"),
      os.path.expanduser("~/nta/nupic.research"),
  ),
}

# Location of requirements.txt for each repo
REQUIREMENTS = {
  "nupic.core": os.path.expanduser(
      "~/nta/nupic.core/bindings/py/requirements.txt"),
  "nupic": os.path.expanduser("~/nta/nupic/requirements.txt"),
  "htmresearch-core": os.path.expanduser("~/nta/htmresearch-core/bindings/py/requirements.txt"),
  "htmresearch": os.path.expanduser("~/nta/htmresearch/requirements.txt"),
}

# Paths that C++ extensions are installed into for each repo
CPP_EXTENSIONS_PATH = {
  "nupic.core": os.path.expanduser("~/nta/nupic.core/bindings/py/src/nupic/bindings"),
  "htmresearch-core": os.path.expanduser("~/nta/htmresearch-core/bindings/py/src/htmresearch_core"),
}

nupicCorePath = os.path.expanduser("~/nta/nupic.core")
CMAKE_EXTRA_OPTIONS = {
  "nupic.core": [],
  "htmresearch-core": ["-DLOCAL_NUPIC_CORE_SOURCE={}".format(nupicCorePath)],
}
