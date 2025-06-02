import numpy as np
import pickle
import pandas as pd
import moose
import matplotlib.pyplot as plt

SOMA_A = 3.14e-8
F = 96485.3329
R = 8.314
celsius = 34
dt = 0.05e-3
ENa = 53e-3
EK = -107e-3
Eh = -0.045
ECa = 0.140
Em = -0.065

#################################
mPower = 3
hPower = 1

m_vhalf_inf, m_slope_inf, m_A, m_B, m_C, m_D, m_E, m_F = -0.04230235, 0.006, -0.04476696, 0.02195916, 0.01651614, 0.04558798, 0.01921329, 0.00093119
h_vhalf_inf, h_slope_inf, h_A, h_B, h_C, h_D, h_E, h_F = -66e-3, -6e-3, -0.07071566,0.02638247,0.01824088,0.06117676,0.0161364, 0.00866348
#################################


Vmin = -0.100
Vmax = 0.100
Vdivs = 3000
# dV = (Vmax-Vmin)/Vdivs
# v = np.arange(Vmin,Vmax, dV)
v = np.linspace(Vmin,Vmax, Vdivs)
Camin = 1e-12
Camax = 3
Cadivs = 4000
# dCa = (Camax-Camin)/Cadivs
# ca = np.arange(Camin,Camax, dCa)
ca = np.linspace(Camin,Camax, Cadivs)

def ChanGate(v,vhalf_inf, slope_inf, A, B, C, D, E, F):
    # alge model
    Inf = 1/(1+np.exp((v-vhalf_inf)/-slope_inf))
    yl = (v-A)/-B
    yr = (v-A)/E
    Tau = (C + (1 + yl/(np.sqrt(1+yl**2)))/2) * (D + (1 + yr/(np.sqrt(1+yr**2)))/2) * F
    Tau[Tau<0.00002] = 0.00002
    return [Inf,Tau]

def dummy_Chan(name):
    dummy = moose.HHChannel( '/library/' + name )
    dummy.Ek = Eh
    dummy.Gbar = 300.0*SOMA_A
    dummy.Gk = 0.0
    dummy.Xpower = mPower
    dummy.Ypower = hPower
    dummy.Zpower = 0
    dummy.useConcentration = 0

    mInf, mTau = ChanGate(m_vhalf_inf, m_slope_inf, m_A, m_B, m_C, m_D, m_E, m_F)
    hInf, hTau = ChanGate(h_vhalf_inf, h_slope_inf, h_A, h_B, h_C, h_D, h_E, h_F)

    xgate = moose.element( dummy.path + '/gateX' )
    xgate.min = Vmin
    xgate.max = Vmax
    xgate.divs = Vdivs
    xgate.tableA = mInf/mTau
    xgate.tableB = 1.0/mTau

    ygate = moose.element( dummy.path + '/gateY' )
    ygate.min = Vmin
    ygate.max = Vmax
    ygate.divs = Vdivs
    ygate.tableA = hInf/hTau
    ygate.tableB = 1.0/hTau

    return dummy


if __name__ == "__main__":
    moose.Neutral('library')
    dummy_Chan('dummy_Chan')
    plt.figure()
    plt.plot(v, moose.element('library/dummy_Chan/gateX').tableA/moose.element('library/dummy_Chan/gateX').tableB, label='mInf')
    plt.plot(v, moose.element('library/dummy_Chan/gateY').tableA/moose.element('library/dummy_Chan/gateY').tableB, label='hInf')
    plt.ylabel('Inf')
    plt.legend()
    plt.grid()
    plt.figure()
    plt.plot(v, 1/moose.element('library/dummy_Chan/gateX').tableB, label='mTau')
    plt.plot(v, 1/moose.element('library/dummy_Chan/gateY').tableB, label='hTau')
    plt.ylabel('Tau')
    plt.legend()
    plt.grid()
    plt.show()