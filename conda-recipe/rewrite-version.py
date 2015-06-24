"""
This script rewrites the version.py and __init__.py files
in simtk/openmmm, so that the library and plugins get loaded correctly
on windows. The latest version of OpenMM works fine without this, but
earlier versions of the library don't work with conda.

The changes are roughly analogous to
https://github.com/pandegroup/openmm/pull/780 and I think finally fixed in master
on https://github.com/pandegroup/openmm/commit/e16acd1bdd225ec0e58291d4489142d82f0662dd
"""
import sys
import os

with open(os.path.join(os.environ['SP_DIR'], 'simtk', 'openmm', 'version.py'), 'w') as f:
    f.write("\nopenmm_library_path = '%s'\n" % os.path.join(os.environ['PREFIX'], 'lib').replace('\\', '\\\\'))

with open(os.path.join(os.environ['SP_DIR'], 'simtk', 'openmm', '__init__.py'), 'w') as f:
    f.write("""

__author__ = "Randall J. Radmer"

import os, os.path
import sys
from simtk.openmm import version

if sys.platform == 'win32':
    _path = os.environ['PATH']
    os.environ['PATH'] = '%(lib)s;%(lib)s\plugins;%(path)s' % {
        'lib': version.openmm_library_path, 'path': _path}

from simtk.openmm.openmm import *
from simtk.openmm.vec3 import Vec3

pluginLoadedLibNames = Platform.loadPluginsFromDirectory(os.path.join(version.openmm_library_path, 'plugins'))

if sys.platform == 'win32':
    os.environ['PATH'] = _path
    del _path

__version__ = Platform.getOpenMMVersion()
""")