# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""

import numpy
import control
import matplotlib.pyplot as plt


def get_Tie_Data(Dist, Generators, Damping, Kg):
    R = [0, 0]
    for gen in Generators:
        R[gen['Area']-1] += 1/gen['R']
    for x in range(len(R)):
        R[x] = 1/R[x]
    D = [Damping[0]['D'], Damping[1]['D']]
    # Tg = [1/Kg[0]/R[0], 1/Kg[1]/R[1]]

    return R, D


def get_TieLine(Δw, Disturbance, Generators, Damping, Base):
    if Disturbance['Area'] == 1:
        area = 2
        ΔPtie_pu = Damping[1]['D']
    else:
        area = 1
        ΔPtie_pu = Damping[0]['D']

    for gen in Generators:
        if gen['Area'] == area:
            ΔPtie_pu += 1/gen['R']

    ΔPtie_pu *= Δw
    ΔPtie = ΔPtie_pu*Base

    if Disturbance['Magnitude'] < 0:  # Higher load than generation
        a1 = area
        a2 = Disturbance['Area']
    else:
        a1 = Disturbance['Area']
        a2 = area

    Ptie = Disturbance['Flow']
    if (a1 == 1 and Disturbance['Magnitude'] > 0) or \
            (a1 == 2 and Disturbance['Magnitude'] < 0):
        Ptie += ΔPtie
    else:
        Ptie -= ΔPtie

    return ΔPtie, ΔPtie_pu, Ptie, a1, a2


def interconnected_frequency_primary(Area, R, D, M, Tch, Kg, Tg, Tl, t, ΔPL):
    mod = interconnected_model(R, D, M, Tch, Kg, Tg, Tl)

    if Area == 1:
        a = 0
        b = 1
    else:
        a = 1
        b = 0
    mod['a'] = a
    mod['b'] = b

    TF = [0, 0]
    for x in range(2):
        TF[x] = control.feedback(mod['A'][x],
                                 mod['1/R'][x]*mod['G'][x]*mod['P'][x])
    TFa = TF[a]/(1 + TF[a]*mod['T'] -
                 TF[a]*TF[b]*mod['T']*mod['T']/(1 + TF[b]*mod['T']))
    TFb = TF[a]*TF[b]*mod['T']/(1+TF[a]*mod['T']) / \
        (1+TF[b]*mod['T']-TF[a]*TF[b]*mod['T']*mod['T']/(1+TF[a]*mod['T']))

    t, Δw1 = control.forced_response(TFa, t, ΔPL)
    t, Δw2 = control.forced_response(TFb, t, ΔPL)

    return Δw1, Δw2, mod


def interconnected_frequency_secondary(mod, Area, ΔPL_value, T):
    # Input signals
    t = numpy.linspace(0, T, 1000)
    Init = 1
    ΔPL = []
    for x in t:
        if x < Init:
            ΔPL.append(0)
        else:
            ΔPL.append(-ΔPL_value)

    # Assigning contingency to an area
    if Area == 1:
        a = 0
        b = 1
    else:
        b = 0
        a = 1
    mod['a'] = a
    mod['b'] = b

    # Developing control equations
    K1 = 1 + mod['A'][a] * mod['G'][a] * mod['P'][a] * \
        (mod['K'][a]*mod['B'][a] + mod['1/R'][a])
    K2 = -mod['A'][a] * (1 + mod['G'][a] * mod['P'][a] * mod['K'][a])
    K3 = -mod['A'][a]
    K4 = 1 + mod['A'][b] * mod['G'][b] * mod['P'][b] * \
        (mod['K'][b] * mod['B'][b] + mod['1/R'][b])
    K5 = mod['A'][b] * (1 + mod['G'][b] * mod['P'][b] * mod['K'][b])

    # Solving for Δw
    TF1 = K3/K2 * (1 + mod['T'] * K5/K4) / \
        (K1/K2 * (1 + mod['T']*K5/K4) - mod['T'])
    t, Δw1 = control.forced_response(TF1, t, ΔPL)

    TF2 = (mod['T'] * K3/K1)/(mod['T'] + K4/K5 * (1 - mod['T'] * K2/K1))
    _, Δw2 = control.forced_response(TF2, t, ΔPL)

    return t, Δw1, Δw2


def interconnected_model(R, D, M, Tch, Kg, Tg, Tl, Beta=[0, 0], Kt=[0, 0]):
    mod = {
        'G': [0, 0],
        'P': [0, 0],
        'A': [0, 0],
        '1/R': [0, 0],
        'B': [0, 0],
        'K': [0, 0]
    }
    for x in range(2):
        mod['G'][x] = control.tf(1, [Tg[x], 1])

        mod['P'][x] = control.tf(1, [Tch[x], 1])

        mod['A'][x] = control.tf(1, [M[x], D[x]])

        mod['1/R'][x] = control.tf(1/R[x], 1)

        mod['B'][x] = control.tf(Beta[x], 1)

        mod['K'][x] = control.tf(Kt[x], [1, 0])

    mod['T'] = control.tf(Tl, [1, 0])

    return mod


def interconnected_power(mod, t, Δw1, Δw2):
    a = mod['a']
    b = mod['b']

    # Solving for tie line flows
    _, Tie = control.forced_response(mod['T'], t, Δw1-Δw2)

    # Get Power (pu) response in Area 1
    _, aux = control.forced_response(mod['B'][a], t, Δw1)
    ACE1 = -Tie - aux
    _, aux1 = control.forced_response(mod['K'][a], t, ACE1)
    _, aux2 = control.forced_response(mod['1/R'][a], t, Δw1)
    _, P1 = control.forced_response(mod['G'][a]*mod['P'][a], t, aux1-aux2)

    # Get Power (pu) response in Area 2
    _, aux = control.forced_response(mod['B'][b], t, Δw2)
    ACE2 = Tie - aux
    _, aux1 = control.forced_response(mod['K'][b], t, ACE2)
    _, aux2 = control.forced_response(mod['1/R'][b], t, Δw2)
    _, P2 = control.forced_response(mod['G'][b]*mod['P'][b], t, aux1-aux2)

    if a == 1:
        Tie *= -1

    return Tie, P1, P2



def plot_Ppu(t, Tie, P1, P2):
    fig = plt.figure(figsize=(12, 3))
    grid = plt.GridSpec(4, 9, hspace=0.2, wspace=0.2)
    Freq = fig.add_subplot(grid[:, 0:4])
    Freq.plot(t, P1, label='ΔPm1')
    Freq.plot(t, P2, label='ΔPm2')
    Freq.set_xlabel('time (s)')
    Freq.set_ylabel('Area ΔPm (pu)')
    plt.legend()
    Freq.grid()

    Line = fig.add_subplot(grid[:, 5:9])
    Line.plot(t, Tie)
    Line.set_xlabel('time (s)')
    Line.set_ylabel('Tie-line P (pu)')
    Line.grid()


def plot_Δw(t, Δw1, Δw2):
    plt.figure(figsize=(12, 3))
    plt.plot(t, Δw1, label='Δw1')
    plt.plot(t, Δw2, label='Δw2')
    plt.xlabel('time (s)')
    plt.ylabel('Δw (rads)')
    plt.grid()
    plt.legend()
    plt.show()


def print_TieLine(ΔPtie, ΔPtie_pu, Ptie, a1, a2):
    print('The disturbace causes power to flow from Area %d to Area %d' % (a1,
                                                                           a2))
    print('ΔPtie: %.4f pu (%.4f MW)' % (abs(ΔPtie_pu), abs(ΔPtie)))
    if Ptie > 0:
        txt1 = 'exporting'
        txt2 = 'to'
    else:
        txt1 = 'importing'
        txt2 = 'from'
    print('As a result Area 1 is currently %s %.4f MW %s Area 2' % (txt1,
                                                                    abs(Ptie),
                                                                    txt2))


def run_DCPF(Connectivity, Load, Generator):
    # Finding slack bus
    for gen in Generator:
        if 'V' in gen.keys() and '𝜃' in gen.keys():
            Slack = gen['Bus'] - 1
            break
    if Slack is None:
        print('The slack bus is missing')
        return False, None, None

    # Getting number of buses
    No_Buses = 0
    for line in Connectivity:
        No_Buses = max([No_Buses, line[0], line[1]])

    # Building Y bus
    M = numpy.zeros((No_Buses-1, No_Buses-1))
    for line in Connectivity:
        y = 1/line[2].imag
        i = line[0] - 1
        j = line[1] - 1

        if i != Slack:
            if i > Slack:
                i -= 1
            M[i, i] += y
            if j != Slack:
                if j > Slack:
                    j -= 1
                M[j, i] -= y
                M[i, j] -= y
                M[j, j] += y

        elif j != Slack:
            if j > Slack:
                j -= 1
            M[j, j] += y

    ΔP = numpy.zeros(No_Buses-1)
    for gen in Generator:
        if 'P' in gen.keys():
            i = gen['Bus']-1
            if i != Slack:
                if i > Slack:
                    i -= 1
                ΔP[i] += gen['P']

    for ld in Load:
        i = ld[0]-1
        if i != Slack:
            if i > Slack:
                i -= 1
            ΔP[i] -= ld[1].real

    # Solve DC flows
    Δ𝜃 = numpy.linalg.inv(M).dot(ΔP)
    𝜃 = numpy.zeros(No_Buses)
    P = numpy.zeros(No_Buses)
    P[Slack] = sum(ΔP)
    i = 0
    for x in range(No_Buses):
        if x != Slack:
            𝜃[x] = Δ𝜃[i]
            P[x] = ΔP[i]
            i += 1

    return True, 𝜃, P


def Visualize_DC(Connectivity, 𝜃, P, Succes):
    if not Succes:
        return

    Base = 100
    No_Buses = len(P)
    print('NET POWER INJECTIONS:')
    for xb in range(No_Buses):
        print('%2.0f) %8.4f MW' % (xb+1, P[xb]*Base))

    print('POWER FLOWS:')
    for line in Connectivity:
        i = line[0]
        j = line[1]
        f = (𝜃[i-1]-𝜃[j-1])/line[2].imag*Base
        print('%2.0f-%2.0f) %8.4f ' % (i, j, f))
    print()





