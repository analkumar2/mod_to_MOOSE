### Helper script that runs the MOOSE part (since NEURON and MOOSE cannot be run simultanously) and saves the results

import sys
import importlib.util
import moose
import numpy as np
import inspect


def import_python_file(filename):
    module_name = filename[:-3] if filename.endswith(".py") else filename
    spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module  # Now you can use module's functions & variables

def list_user_functions(module):
    """List only user-defined functions, excluding built-in and imported ones."""
    return [
        name for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__
    ]

MOOSEkinmodule = import_python_file(sys.argv[1])
chanfunc = getattr(MOOSEkinmodule, list_user_functions(MOOSEkinmodule)[0])

moose.Neutral('library')
Chan = chanfunc('Chan')

if Chan.Xpower>=1:
    xgate = moose.element( Chan.path + '/gateX' )
    v = np.linspace(xgate.min, xgate.max, xgate.divs+1)
    Xinf = (xgate.tableA/xgate.tableB)**Chan.Xpower
    Xtau = 1/xgate.tableB
    np.save('X.npy', [v,Xinf, Xtau])

if Chan.Ypower>=1:
    ygate = moose.element( Chan.path + '/gateY' )
    v = np.linspace(ygate.min, ygate.max, ygate.divs+1)
    Yinf = (ygate.tableA/ygate.tableB)**Chan.Ypower
    Ytau = 1/ygate.tableB
    np.save('Y.npy', [v,Yinf, Ytau])

if Chan.Zpower>=1 and Chan.useConcentration is False:
    zgate = moose.element( Chan.path + '/gateZ' )
    v = np.linspace(zgate.min, zgate.max, zgate.divs+1)
    Zinf = (zgate.tableA/zgate.tableB)**Chan.Zpower
    Ztau = 1/zgate.tableB
    np.save('Z.npy', [v,Zinf, Ztau])


