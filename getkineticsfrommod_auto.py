## v5: Provide the powers of m and h gates in order as sys.argv[2]

import shutil

try:
    shutil.rmtree('x86_64')
except:
    pass

import numpy as np
import matplotlib.pyplot as plt
import brute_curvefit
import sys
import tempfile
import re
import os
import pynmodl 
from pprint import pprint
from textx.metamodel import metamodel_from_file

#### Parsing the nmodl file to extract inf and tau variables ###
mm = metamodel_from_file(pynmodl.__path__[0]+'/grammar/nmodl.tx')
blocks = mm.model_from_file(sys.argv[1]).blocks
powerlist = [int(x) for x in sys.argv[2].split(',')]

inflist_forRANGEwrite = []
taulist_forRANGEwrite = [] #For modifying the mod file. Two separate lists are needed because sometimes the code defines variables in a list.
inflist = []
taulist = []
for block in blocks:
    if type(block).__name__ == 'Assigned':
        for i in block.assigneds:
            if 'inf' in i.name or 'Inf' in i.name:
                inflist_forRANGEwrite.append(i.name)
                if i.len == 0:
                    inflist.append(i.name)
                else:
                    for j in range(i.len):
                        inflist.append(i.name+f'[{j}]')
            elif 'tau' in i.name or 'Tau' in i.name:
                taulist_forRANGEwrite.append(i.name)
                if i.len == 0:
                    taulist.append(i.name)
                else:
                    for j in range(i.len):
                        taulist.append(i.name+f'[{j}]')
    if type(block).__name__ == 'Neuron':
        for statement in block.statements:
            if type(statement).__name__ == 'Suffix':
                suffix = statement.suffix
                print(suffix)
        print(block)

print(inflist_forRANGEwrite)
print(taulist_forRANGEwrite)
#################################################################
##### add the RANGE line for taus and infs in a temporary file ###############
def add_taun_tauf_after_range(original_file_path):
    # Open the original file
    with open(original_file_path, 'r') as original_file:
        found_useion = False
        inside_neuron_section = False

        # Create a list to store the lines to be written to the temporary file
        new_content = []

        # Find the line with 'RANGE' in the original file and add 'RANGE taun, tauf' after it
        for line in original_file:
            if 'GLOBAL' in line:
                line = line.replace('GLOBAL', 'RANGE')
            new_content.append(line)
            if line.startswith("NEURON") and "{" in line:
                inside_neuron_section = True
            elif inside_neuron_section and "}" in line:
                inside_neuron_section = False                
            if inside_neuron_section and 'USEION' in line and not found_useion:
                new_content.append('    RANGE ' + ', '.join(inflist_forRANGEwrite) + '\n')
                new_content.append('    RANGE ' + ', '.join(taulist_forRANGEwrite) + '\n')
                found_useion = True
            # print(new_content[-1])


    # Create a temporary file
    # with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
    with open(f'temp/{os.path.basename(original_file_path)}', 'w') as temp_file:
        # Write the modified content back to the temporary file
        with open(temp_file.name, 'w') as temp_file_write:
            temp_file_write.writelines(new_content)

    # Print the path of the temporary file
    return f'temp/{os.path.basename(original_file_path)}'

modfile_corrected = add_taun_tauf_after_range(sys.argv[1])
print(modfile_corrected)
####################################################################################################
os.system(f'nrnivmodl {modfile_corrected}')
from neuron import h,gui

h.celsius = 32
soma = h.Section(name='soma')
soma.insert(suffix)

clamp = h.SEClamp(soma(0.5))
clamp.rs = 1e-3 # series resistance should be much smaller than input resistance of the cell
clamp.dur1 = 1e9

cmd = h.Vector(np.linspace(-100,100,3000))
cmd.play(clamp._ref_amp1, 2000/3000)
h.v_init = -100


# minf_vec = h.Vector()
# mtau_vec = h.Vector()             # Membrane potential vector
infvec_list = [h.Vector() for i in range(len(inflist))]
tauvec_list = [h.Vector() for i in range(len(taulist))]
v_vec = h.Vector()
t_vec = h.Vector()             # Time stamp vector

v_vec.record(soma(0.5)._ref_v)

for i,infrec in enumerate(infvec_list):
    exec(f"infrec.record(soma(0.5).{suffix}._ref_{inflist[i]})")
for i,taurec in enumerate(tauvec_list):
    exec(f"taurec.record(soma(0.5).{suffix}._ref_{taulist[i]})")

# minf_vec.record(soma(0.5).kdr._ref_ninf)
# mtau_vec.record(soma(0.5).kdr._ref_taun)

t_vec.record(h._ref_t)


h.finitialize()
h.tstop = 2000
h.run()

plt.plot(t_vec, v_vec)
plt.show()

for i in range(len(inflist)):
    plt.plot(v_vec, infvec_list[i], label=inflist[i])
plt.legend()
plt.show()

for i in range(len(taulist)):
    plt.plot(v_vec, tauvec_list[i], label=taulist[i])
plt.show()


##### Parameterized plots ##################################
def ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
  # alge model
    Inf = 1/(1+np.exp((v-vhalf_inf)/-slope_inf))
    yl = (v-A)/-B
    yr = (v-A)/E
    Tau = (C + (1 + yl/(np.sqrt(1+yl**2)))/2) * (D + (1 + yr/(np.sqrt(1+yr**2)))/2) * F
    Tau[Tau<0.00002] = 0.00002
    return [Inf,Tau]

def wr_ChanGate_inf(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
    return ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F)[0]

def wr_ChanGate_tau(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
    return ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F)[1]

for i in range(len(inflist)):
    paramfitted_inf, error = brute_curvefit.brute_scifit(wr_ChanGate_inf, np.array(v_vec)*1e-3, np.array(infvec_list[i])**(1/powerlist[i]), restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.1,0.1,0.5,0.5,1]])
    plt.plot(v_vec, np.array(infvec_list[i])**(1/powerlist[i]), label='ori')
    plt.plot(v_vec, wr_ChanGate_inf(np.array(v_vec)*1e-3, *paramfitted_inf), label='fitted')
    print(inflist[i], paramfitted_inf[:2])
    plt.legend()
    plt.show()

for i in range(len(taulist)):
    paramfitted_tau, error = brute_curvefit.brute_scifit(wr_ChanGate_tau, np.array(v_vec)*1e-3, np.array(tauvec_list[i])*1e-3, restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.1,0.1,0.5,0.5,1]])
    plt.plot(v_vec, np.array(tauvec_list[i])*1e-3, label='ori')
    plt.plot(v_vec, wr_ChanGate_tau(np.array(v_vec)*1e-3, *paramfitted_tau), label='fitted')
    print(taulist[i], paramfitted_tau[2:])
    plt.legend()
    plt.show()




# paramfitted_inf, error = brute_curvefit.brute_scifit(wr_ChanGate_inf, np.array(v_vec)*1e-3, np.array(minf_vec), restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.1,0.1,0.5,0.5,1]])

# plt.plot(v_vec, minf_vec, label='ori')
# plt.plot(v_vec, wr_ChanGate_inf(np.array(v_vec)*1e-3, *paramfitted_inf), label='fitted')
# print(paramfitted_inf)
# plt.legend()
# plt.show()

# paramfitted_tau, error = brute_curvefit.brute_scifit(wr_ChanGate_tau, np.array(v_vec)*1e-3, np.array(mtau_vec)*1e-3, restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 1,0.5,0.5,0.5,0.5,1]], ntol = 10000, returnnfactor = 0.001)

# plt.plot(v_vec, np.array(mtau_vec)*1e-3, label='ori')
# plt.plot(v_vec, wr_ChanGate_tau(np.array(v_vec)*1e-3, *paramfitted_tau), label='fitted')
# print(paramfitted_tau)
# plt.legend()
# plt.show()

# paramfitted_inf, error = brute_curvefit.brute_scifit(wr_ChanGate_inf, np.array(v_vec)*1e-3, np.array(hinf_vec), restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.1,0.1,0.5,0.5,1]])

# plt.plot(v_vec, hinf_vec, label='ori')
# plt.plot(v_vec, wr_ChanGate_inf(np.array(v_vec)*1e-3, *paramfitted_inf), label='fitted')
# print(paramfitted_inf)
# plt.legend()
# plt.show()

# paramfitted_tau, error = brute_curvefit.brute_scifit(wr_ChanGate_tau, np.array(v_vec)*1e-3, np.array(htau_vec)*1e-3, restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 1,0.5,0.5,0.5,0.5,1]], ntol = 10000, returnnfactor = 0.001)

# plt.plot(v_vec, np.array(htau_vec)*1e-3, label='ori')
# plt.plot(v_vec, wr_ChanGate_tau(np.array(v_vec)*1e-3, *paramfitted_tau), label='fitted')
# print(paramfitted_tau)
# plt.legend()
# plt.show()

