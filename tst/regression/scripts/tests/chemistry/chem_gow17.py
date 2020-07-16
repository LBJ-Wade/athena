#regression test for equilibrium chemistry and temperature
#with chemical network gow17, compare to know solution.

# Modules
import logging
import numpy as np                             # standard Python module for numerics
import sys                                     # standard Python module to change path
import scripts.utils.athena as athena          # utilities for running Athena++
import scripts.utils.comparison as comparison  # more utilities explicitly for testing
sys.path.insert(0, '../../vis/python')         # insert path to Python read scripts
import athena_read                             # utilities for reading Athena++ data
import os
logger = logging.getLogger('athena' + __name__[7:])  # set logger name based on module

def prepare(**kwargs):
    if os.environ['CXX']:
        cxx = os.environ['CXX']
    else:
        cxx = 'g++'
    athena.configure(
        prob='chem_uniform_radcr',
        chemistry='gow17', 
        radiation='const',
        cxx=cxx,
        cvode_path=os.environ['CVODE_PATH']
        )
    athena.make()

def run(**kwargs):
    arguments = [ 
            'problem/G0=1e-6',
            ]
    athena.run('chemistry/athinput.chem_gow17', arguments)

def analyze():
    err_control = 1e-6
    gam1 = 1.666666666666667 - 1.
    nH = 1.0921e+02
    unit_E_cgs = 1.67e-24 * 1.4 * 1e10
    _,_,_,data_ref = athena_read.vtk('data/chem_gow17_G1e-6.vtk')
    _,_,_,data_new = athena_read.vtk('bin/chem_gow17.block0.out1.00010.vtk')
    species = ["He+", "OHx", "CHx", "CO", "C+", "HCO+", "H2", "H+", "H3+", "H2+", 
               "O+", "Si+"]
    ns = len(species)
    err_all = np.zeros(ns+1)
    for i in np.arange(ns):
        s = species[i]
        xs_ref = data_ref[s]
        xs_new = data_new["r"+s]
        err_all[i] = (abs(xs_ref - xs_new) / abs(xs_ref) ).max()
        print(s, err_all[i])
    E_ref = data_ref["E"]
    E_new = data_new["press"]/gam1 * unit_E_cgs / nH
    err_all[ns] = (abs(E_ref - E_new) / abs(E_ref) ).max()
    print("E", err_all[ns])
    err_max = err_all.max()
    if err_max < err_control:
       return True
    else:
        print("err_max", err_max)
        return False
