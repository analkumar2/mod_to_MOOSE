# ## exec(open('getkineticsfrommod.py').read())
# ## sudo nrnivmodl '../../Compilations/ExistingModels/Poolos2002/lamotrigine/na3nn.mod'

from neuron import h,gui
import numpy as np
import matplotlib.pyplot as plt
import brute_curvefit

def ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
	# alge model
    Inf = 1/(1+np.exp((v-vhalf_inf)/-slope_inf))
    yl = (v-A)/-B
    yr = (v-A)/E
    Tau = (C + (1 + yl/(np.sqrt(1+yl**2)))/2) * (D + (1 + yr/(np.sqrt(1+yr**2)))/2) * F
    Tau[Tau<0.00002] = 0.00002
    return [Inf,Tau]

h.celsius = 32
soma = h.Section(name='soma')
# # soma.insert('hha2')
# # soma.insert('kdr')
# # soma.insert('cal')
# soma.insert('can')
# soma.insert('cat')
# # soma.insert('calH')
# # soma.insert('car')
# # soma.insert('cat')
# # soma.insert('car_mag')
# # soma.insert('Nap_Et2')
# # soma.insert('NaTg')
# # soma.insert('nax')
# # soma.insert('na3n')
# soma.insert('kdb')
# soma.insert('hd')
# soma.insert('h')
# soma.insert('Kv3_1')
# soma.insert('NaTs')
# # soma.insert('kmb')
# # soma.insert('cagk')
# # soma.insert('kap')
# soma.insert('kdr')
# # soma.insert('SKv3_1')
# # soma.insert('sk')
# soma.insert('Im')
# soma.insert('K_T')
# soma.insert('K_P')
# soma.insert('iNas')
# soma.insert('na3')
# soma.insert('Nap')
soma.insert('Ca_HVA')

# # h.cai0_ca_ion = 5e-5

clamp = h.SEClamp(soma(0.5))
clamp.rs = 1e-3 # series resistance should be much smaller than input resistance of the cell
clamp.dur1 = 1e9

cmd = h.Vector(np.linspace(-100,100,3000))
cmd.play(clamp._ref_amp1, 2000/3000)
h.v_init = -100


minf_vec = h.Vector()
mtau_vec = h.Vector()             # Membrane potential vector
hinf_vec = h.Vector()
htau_vec = h.Vector()
# sinf_vec = h.Vector()
# stau_vec = h.Vector()
v_vec = h.Vector()
t_vec = h.Vector()             # Time stamp vector
# iKT_vec = h.Vector()
# iKP_vec = h.Vector()
# minf2_vec = h.Vector()
# mtau2_vec = h.Vector()             # Membrane potential vector
# hinf2_vec = h.Vector()
# htau2_vec = h.Vector()
# sinf2_vec = h.Vector()
# stau2_vec = h.Vector()

v_vec.record(soma(0.5)._ref_v)
# # minf_vec.record(soma(0.5).cagk._ref_oinf)
# # mtau_vec.record(soma(0.5).cagk._ref_tau)
# # minf_vec.record(soma(0.5).cal._ref_inf)
# # mtau_vec.record(soma(0.5).cal._ref_tau_m)
# # minf_vec.record(soma(0.5).cat._ref_hinf)
# # mtau_vec.record(soma(0.5).cat._ref_tauh)
# # minf_vec.record(soma(0.5).car._ref_inf[1])
# # mtau_vec.record(soma(0.5).car._ref_tau[1])
# # minf_vec.record(soma(0.5).nax._ref_minf)
# # mtau_vec.record(soma(0.5).nax._ref_mtau)
# # minf_vec.record(soma(0.5).na3n._ref_minf)
# # mtau_vec.record(soma(0.5).na3n._ref_mtau)
# # hinf_vec.record(soma(0.5).na3n._ref_hinf)
# # htau_vec.record(soma(0.5).na3n._ref_htau)
# # minf_vec.record(soma(0.5).kmb._ref_inf)
# # mtau_vec.record(soma(0.5).kmb._ref_tau)
# minf_vec.record(soma(0.5).h._ref_linf)
# mtau_vec.record(soma(0.5).h._ref_taul)
# minf_vec.record(soma(0.5).Kv3_1._ref_mInf)
# mtau_vec.record(soma(0.5).Kv3_1._ref_mTau)
# minf_vec.record(soma(0.5).NaTs._ref_mInf)
# mtau_vec.record(soma(0.5).NaTs._ref_mTau)
# hinf_vec.record(soma(0.5).NaTs._ref_hInf)
# htau_vec.record(soma(0.5).NaTs._ref_hTau)
# iNats_vec.record(soma(0.5).NaTs._ref_ina)
# minf_vec.record(soma(0.5).kdb._ref_ninf)
# mtau_vec.record(soma(0.5).kdb._ref_taun)
# # minf_vec.record(soma(0.5).kap._ref_ninf)
# # mtau_vec.record(soma(0.5).kap._ref_taun)
# # minf_vec.record(soma(0.5).kap._ref_linf)
# # mtau_vec.record(soma(0.5).kap._ref_taul)
# minf_vec.record(soma(0.5).kdr._ref_ninf)
# mtau_vec.record(soma(0.5).kdr._ref_taun)
# # minf_vec.record(soma(0.5).SKv3_1._ref_mInf)
# # mtau_vec.record(soma(0.5).SKv3_1._ref_mTau)
# # ninf_vec.record(soma(0.5).hha2._ref_inf[2])
# # ntau_vec.record(soma(0.5).hha2._ref_tau[2])
# # hinf_vec.record(soma(0.5).hha2._ref_inf[1])
# # htau_vec.record(soma(0.5).hha2._ref_tau[1])
# minf_vec.record(soma(0.5).Im._ref_mInf)
# mtau_vec.record(soma(0.5).Im._ref_mTau)
# iKP_vec.record(soma(0.5).K_P._ref_ik)
# iKT_vec.record(soma(0.5).K_T._ref_ik)
# minf_vec.record(soma(0.5).iNas._ref_minf)
# mtau_vec.record(soma(0.5).iNas._ref_mtau)
# hinf_vec.record(soma(0.5).iNas._ref_hinf)
# htau_vec.record(soma(0.5).iNas._ref_htau)
# sinf_vec.record(soma(0.5).iNas._ref_hinf)
# stau_vec.record(soma(0.5).iNas._ref_htau)
# minf2_vec.record(soma(0.5).na3._ref_minf)
# mtau2_vec.record(soma(0.5).na3._ref_mtau)
# hinf2_vec.record(soma(0.5).na3._ref_hinf)
# htau2_vec.record(soma(0.5).na3._ref_htau)
# sinf2_vec.record(soma(0.5).na3._ref_sinf)
# stau2_vec.record(soma(0.5).na3._ref_taus)
minf_vec.record(soma(0.5).Ca_HVA._ref_mInf)
mtau_vec.record(soma(0.5).Ca_HVA._ref_mTau)
hinf_vec.record(soma(0.5).Ca_HVA._ref_hInf)
htau_vec.record(soma(0.5).Ca_HVA._ref_hTau)
t_vec.record(h._ref_t)


h.finitialize()
h.tstop = 2000
h.run()

# plt.plot(t_vec, v_vec)
# plt.show()

fig, axs = plt.subplots(2,1)
axs[0].plot(v_vec, minf_vec)
axs[0].plot(v_vec, hinf_vec)
# axs[0].plot(v_vec, minf2_vec, label='minf')
# axs[0].plot(v_vec, np.array(minf2_vec)**3, label='minf**3')
# axs[0].plot(v_vec, hinf2_vec)
axs[0].legend()
axs[0].grid(visible=True, which='both')

axs[1].plot(v_vec, mtau_vec)
axs[1].plot(v_vec, htau_vec)
# axs[1].plot(v_vec, mtau2_vec)
# axs[1].plot(v_vec, htau2_vec)
axs[1].grid(visible=True, which='both')
plt.show()

def wr_ChanGate_inf(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
	return ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F)[0]

def wr_ChanGate_tau(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
	return ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F)[1]

# Vmin = -0.100
# Vmax = 0.100
# Vdivs = 3000
# # v_vec = 
# # minf_vec = 
# # mtau_vec =


### minf #########
paramfitted_inf, error = brute_curvefit.brute_scifit(wr_ChanGate_inf, np.array(v_vec)*1e-3, np.array(minf_vec), restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.1,0.1,0.5,0.5,1]])

plt.plot(v_vec, minf_vec, label='ori')
plt.plot(v_vec, wr_ChanGate_inf(np.array(v_vec)*1e-3, *paramfitted_inf), label='fitted')
print('m_vhalf_inf, m_slope_inf', repr(paramfitted_inf[:2]))
plt.legend()
plt.show()


### mtau ##########
restrict = [[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.5,0.5,0.5,0.5,1]]
paramfitted_tau, error = brute_curvefit.brute_scifit(wr_ChanGate_tau, np.array(v_vec)*1e-3, np.array(mtau_vec)*1e-3, restrict=restrict, ntol = 10000, returnnfactor = 0.001)

plt.plot(v_vec, np.array(mtau_vec)*1e-3, label='ori')
plt.plot(v_vec, wr_ChanGate_tau(np.array(v_vec)*1e-3, *paramfitted_tau), label='fitted')
print('m_A, m_B, m_C, m_D, m_E, m_F', repr(paramfitted_inf[2:]))
plt.legend()
plt.show()


### hinf ##########
paramfitted_inf, error = brute_curvefit.brute_scifit(wr_ChanGate_inf, np.array(v_vec)*1e-3, np.array(hinf_vec), restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 0.1,0.1,0.1,0.5,0.5,1]])

plt.plot(v_vec, hinf_vec, label='ori')
plt.plot(v_vec, wr_ChanGate_inf(np.array(v_vec)*1e-3, *paramfitted_inf), label='fitted')
print('h_vhalf_inf, h_slope_inf', repr(paramfitted_inf[:2]))
plt.legend()
plt.show()


### htau ##########
paramfitted_tau, error = brute_curvefit.brute_scifit(wr_ChanGate_tau, np.array(v_vec)*1e-3, np.array(htau_vec)*1e-3, restrict=[[-0.1,-0.1, -0.1,0,0,0,0,0],[0.1,0.1, 1,0.5,0.5,0.5,0.5,1000]], ntol = 10000, returnnfactor = 0.001)

plt.plot(v_vec, np.array(htau_vec)*1e-3, label='ori')
plt.plot(v_vec, wr_ChanGate_tau(np.array(v_vec)*1e-3, *paramfitted_tau), label='fitted')
print('h_A, h_B, h_C, h_D, h_E, h_F', repr(paramfitted_inf[2:]))
plt.legend()
plt.show()