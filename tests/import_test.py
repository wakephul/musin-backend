# import nest
# import bsb #scaffold
# # from bsb import Scaffold
# from bsb.config import JSONConfig

# nest.Install('cerebmodule')
# nest.Install('extracerebmodule')

import imp
import os
MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')

def package_contents(package_name):
    file, pathname, description = imp.find_module(package_name)
    if file:
        raise ImportError('Not a package: %r', package_name)
    # Use a set because some may be both source and compiled.
    return set([os.path.splitext(module)[0]
        for module in os.listdir(pathname)
        if module.endswith(MODULE_EXTENSIONS)])

print(package_contents('bsb'))