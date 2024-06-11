# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""

import mplcursors
import numpy
import matplotlib.pyplot as plt
import control


def control_model(ΔPL_value, R, D, M, Tch, Tg, T):
    import control
    TF = get_control_model(R, D, M, Tch, Tg)

    t = numpy.linspace(0, T, 1000)

    ΔPL = get_step(t, 1, ΔPL_value)

    t, Δw = control.forced_response(TF, t, ΔPL)

    return t, Δw


def get_control_model(R, D, M, Tch, Tg):
    Governor = control.tf(1, [Tg, 1])

    Generator = control.tf(1, [Tch, 1])

    Load = control.tf(1, [M, D])

    R_inv = control.tf(1, R)

    return control.feedback(Load, R_inv*Governor*Generator)


def get_pu(Dist, Gen, Load, Base, F):
    import copy
    Disturbance = copy.deepcopy(Dist)
    Disturbance['Magnitude'] /= Base

    Generators = copy.deepcopy(Gen)
    xg = 0
    for gen in Generators:
        R = gen['R']
        if gen['Units'] == 'Hz/MW':
            R *= Base/F
        else:
            if gen['Units'] == '%':
                R /= 100

            if 'Base' in gen.keys():
                R *= Base/gen['Base']
            else:
                R *= Base/gen['Capacity']

        Generators[xg]['R'] = R
        Generators[xg]['Units'] = 'pu'
        Generators[xg]['Base'] = Base
        xg += 1

    Damping = copy.deepcopy(Load)
    xd = 0
    for d in Load:
        D = d['D']
        if d['Units'] == 'MW/Hz':
            D *= F/Base
        else:
            if d['Units'] == '%':
                D /= 100

            if 'Base' in d.keys():
                D *= d['Base']/Base
        Damping[xd]['D'] = D
        Damping[xd]['Base'] = Base
        Damping[xd]['Units'] = 'pu'
        xd += 1

    return Disturbance, Generators, Damping


def get_Primary_Response(Dist, Gen, Load, Base, F):
    print('A disturbance occurred in Area %d' % Dist['Area'])
    if Dist['Magnitude'] > 0:
        txt = 'higher'
    else:
        txt = 'lower'
    print('As a result generation is suddenlly %s than demand by %.4f MW'
          % (txt, abs(Dist['Magnitude'])))
    print()

    Disturbance, Generators, Damping = get_pu(Dist, Gen, Load, Base, F)
    print('Disturbance: %.4f MW (%.4f pu)' %
          (Dist['Magnitude'], Disturbance['Magnitude']))
    No_Generators = len(Generators)
    for xg in range(No_Generators):
        gen = Generators[xg]

        print('G%d) Area%d, Capacity: %10.2f MW, R:%10.4f pu, Output:%10.2f MW'
              % (xg+1, gen['Area'], gen['Capacity'], gen['R'], gen['Output']))
    No_Areas = len(Damping)
    for xd in range(No_Areas):
        damp = Damping[xd]
        print('L%d) Area%d, D: %.4f pu' % (xd+1, xd+1, damp['D']))
    print('*Assuming a %d MVA base\n' % Generators[0]['Base'])

    Δw, Δf, Ff = get_Δw(Disturbance, Generators, Damping, F)
    print('The frequency changed by ', end='')
    print('%.4f pu (%.4f Hz), so the new freqency is %.4f Hz' % (Δw, Δf, Ff))

    print('           ∆Pm and D∆ω     Operation')
    print('          (pu)       (MW)       (MW)')
    xg = 0
    Response = 0
    for gen in Generators:
        if 'Output' in Gen[xg].keys():
            Opt = Gen[xg]['Output']
        else:
            Opt = 0

        pu = -Δw/gen['R']
        prim = Base*pu
        xg += 1
        if 'ΔPref' in gen.keys():
            sec = gen['Secondary']*Base
        else:
            sec = 0
        gen['Output'] = Opt+prim+sec
        Response += prim+sec
        print('G%d) %10.4f %10.4f %10.4f (%10.4f+%10.4f+%10.4f)'
              % (xg, pu, prim, gen['Output'], Opt, prim, sec))

    xd = 0
    for damp in Damping:
        xd += 1
        Response -= damp['D']*Δw*Base
        print('L%d) %10.4f %10.4f' % (xd, damp['D']*Δw, damp['D']*Δw*Base))
    print('All:           %10.4f' % Response)


def get_step(t, Init, Val):
    Dt = []
    for x in t:
        if x < Init:
            Dt.append(0)
        else:
            Dt.append(Val)
    return Dt


def get_Δw(Disturbance, Generators, Damping, F):
    Δw = 0
    for d in Damping:
        Δw += d['D']

    for gen in Generators:
        Δw += 1/gen['R']

    Dst = Disturbance['Magnitude']
    for gen in Generators:
        if 'ΔPref' in gen.keys():
            gen['Secondary'] = gen['ΔPref']*gen['Capacity']/gen['Base']
            Dst += gen['Secondary']
    Δw = Dst/Δw
    Δf = Δw*F
    Ff = F+Δf

    return Δw, Δf, Ff


def plot_control(y, t):
    plt.figure(figsize=(7, 3))
    plt.plot(t, y)
    plt.xlabel('time (s)')
    plt.ylabel('amplitude')
    plt.grid()
    plt.show()


def plot_ΔPm(Δf_check, ΔPref_List, R_List, ΔPL_List, D_List, ΔPm_List,
             Δf_List):

    plt.figure(figsize=(7, 3))

    # Adding generators
    No_Gens = len(ΔPref_List)
    for x in range(No_Gens):
        ΔPref = ΔPref_List[x]
        R = R_List[x]
        lbl = 'G' + str(x+1) + ', ΔPref=' + str(ΔPref) + ', R=' + str(R)
        ΔPm = []
        for Δf in Δf_List:
            ΔPm.append(ΔPref - 1/R*Δf)
        plt.plot(ΔPm, Δf_List, label=lbl)
        print('ΔPm%d: %10.4f (pu)' % (x+1, ΔPref-1/R*Δf_check))

    # Adding loads
    No_Loads = len(ΔPL_List)
    for x in range(No_Loads):
        ΔPL = ΔPL_List[x]
        D = D_List[x]
        lbl = 'L' + str(x+1) + ', ΔPL=' + str(ΔPL) + ', D=' + str(D)
        ΔPe = []
        for Δf in Δf_List:
            ΔPe.append(ΔPL + D*Δf)
        plt.plot(ΔPe, Δf_List, label=lbl)
        print('ΔPe%d: %10.4f (pu)' % (x+1, ΔPL + D*Δf_check))

    plt.plot(ΔPm_List, [Δf_check, Δf_check], linestyle='dashed',
             label='Pimary response')
    plt.xlim(ΔPm_List)
    plt.grid()
    plt.legend()
    plt.ylabel('Δf [pu]')
    if No_Gens > 0:
        if No_Loads > 0:
            plt.xlabel('ΔPm and ΔPe [pu]')
        else:
            plt.xlabel('ΔPm [pu]')
    else:
        plt.xlabel('ΔPe [pu]')
    plt.show()

    mplcursors.cursor()





