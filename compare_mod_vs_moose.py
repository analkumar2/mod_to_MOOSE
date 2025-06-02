### Here we load the mod file and the corresponding MOOSE kinetics file to confirm that they respond the same.
### usage: python3 compare_mod_vs_moose.py suffix MOOSEfile.py infgatenames taugatenames powers
### eg: python3 compare_mod_vs_moose.py Nap Na_P_Chan_allen_exact.py mInf,hInf hTau 2,1


import sys
from neuron import h,gui
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
import importlib.util
import moose
import inspect
import subprocess

###############################################################################################
h.celsius = 32
soma = h.Section(name='soma')


soma.insert(sys.argv[1])

clamp = h.SEClamp(soma(0.5))
clamp.rs = 1e-3 # series resistance should be much smaller than input resistance of the cell
clamp.dur1 = 1e9

cmd = h.Vector(np.linspace(-100,100,3000))
cmd.play(clamp._ref_amp1, 2000/3000)
h.v_init = -100

infgates = sys.argv[3].split(',')
taugates = sys.argv[4].split(',')

infvectors = {}
for inf in infgates:
    infvectors[inf] = h.Vector()
    a = getattr(soma(0.5), f'{sys.argv[1]}')
    b = getattr(a, f'_ref_{inf}')
    infvectors[inf].record(b)

tauvectors = {}
for tau in taugates:
    tauvectors[tau] = h.Vector()
    a = getattr(soma(0.5), f'{sys.argv[1]}')
    b = getattr(a, f'_ref_{tau}')
    tauvectors[tau].record(b)

powerlist = sys.argv[5].split(',')


v_vec = h.Vector()
t_vec = h.Vector()             # Time stamp vector

t_vec.record(h._ref_t)
v_vec.record(soma(0.5)._ref_v)

h.finitialize()
h.tstop = 2000
h.run()

plt.plot(t_vec*1e-3, v_vec*1e-3)
plt.show()

fig, ax = plt.subplots(2,1, sharex=True)

for power,inf in zip(powerlist, infvectors.keys()):
    ax[0].plot(v_vec*1e-3, np.array(infvectors[inf])**int(power), c='C6', label='mod')

for power,tau in zip(powerlist, tauvectors.keys()):
    ax[1].plot(v_vec*1e-3, np.array(tauvectors[tau])*1e-3, c='C6', label='mod')

################################################################################
subprocess.run(["python3", "compare_mod_vs_moose_helper.py", sys.argv[2]])

for gatefile in ['X.npy', 'Y.npy', 'Z.npy'][:len(infvectors)]:
    v,mooseinf, moosetau = np.load(gatefile)
    ax[0].plot(v, mooseinf, c='C2', ls='--', label='MOOSE')
    ax[1].plot(v, moosetau, c='C2', ls='--', label='MOOSE')

ax[0].set_ylabel('Inf')
ax[0].legend()
ax[0].grid()

ax[1].set_ylabel('Tau')
ax[1].legend()
ax[1].grid()


plt.show()
