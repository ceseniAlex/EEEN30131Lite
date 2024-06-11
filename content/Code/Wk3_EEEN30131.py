# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""

import cmath
import math
import numpy


def develop_J_V(Dt_Raw, V):
    Dt = Dt_Raw[0]
    # PQ = Dt_Raw[1]
    bus = Dt_Raw[2]
    txt = Dt_Raw[3]

    print('∂Δ%s/∂V%d = ' % (get_string(txt, bus), V+1), end='')
    flg = False
    for part in range(len(Dt)):
        flg = develop_ΔPQ_V(Dt[part], V, flg)
    if not flg:
        print('0')
    else:
        print()


def develop_J_𝜃(Dt_Raw, 𝜃):
    '''Develop equations ∂P/Q with respect to 𝜃'''
    Dt = Dt_Raw[0]
    # PQ = Dt_Raw[1]
    bus = Dt_Raw[2]
    txt = Dt_Raw[3]

    print('∂Δ%s/∂𝜃%d = ' % (get_string(txt, bus), 𝜃+1), end='')
    flg = False
    for part in range(len(Dt)):
        flg = develop_ΔPQ_𝜃(Dt[part], 𝜃, flg)
    if not flg:
        print('0')
    else:
        print()


def develop_Jacobian(P_Data, Q_Data, Bus_Type, Generator):
    J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All = get_Imp_Unk(Bus_Type, Generator)

    print('The implicit equations correspond to:')
    for bus in J_P:
        print('P'+str(bus+1), end=' ')
    for bus in J_Q:
        print('Q'+str(bus+1), end=' ')

    print('\nThe unknown variables are:')
    for bus in J_𝜃:
        print('𝜃'+str(bus+1), end=' ')
    for bus in J_V:
        print('V'+str(bus+1), end=' ')

    print('\n\nVector of missmatches')
    for bus in J_P:
        develop_ΔPQ(P_Data[bus])
    for bus in J_Q:
        develop_ΔPQ(Q_Data[bus])

    print('\nEquations that form the Jacobian matrix')
    for bus in J_P:
        for 𝜃 in J_𝜃:
            develop_J_𝜃(P_Data[bus], 𝜃)
        for 𝜃 in J_V:
            develop_J_V(P_Data[bus], 𝜃)
        print()
    for bus in J_Q:
        for 𝜃 in J_𝜃:
            develop_J_𝜃(Q_Data[bus], 𝜃)
        for 𝜃 in J_V:
            develop_J_V(Q_Data[bus], 𝜃)
        print()


def develop_ΔPQ(Dt_Raw):
    Dt = Dt_Raw[0]
    PQ = Dt_Raw[1]
    bus = Dt_Raw[2]
    txt = Dt_Raw[3]

    print('Δ%s = ' % get_string(txt, bus), end='')
    flg = False
    for part in range(len(Dt)):
        if Dt[part]['val1'] > 0 and flg:
            print(' + ', end='')
        flg = True
        develop_ΔPQ_string(Dt[part])

    if PQ is None:
        print(' - %s', get_string(txt, bus))
    else:
        if PQ < 0:
            print(' + %.4f' % (-1*PQ))
        else:
            print(' - %.4f' % PQ)


def develop_ΔPQ_string(Dt):
    Str = ''
    if Dt['V1'] is not None:
        Str += get_string('V', Dt['V1'])
    if Dt['V2'] is not None:
        if Dt['V1'] == Dt['V2']:
            Str += '\u00b2'
        else:
            Str += get_string('V', Dt['V2'])

    StrA = ''
    if Dt['𝜃A1'] is not None:
        StrA = Dt['scA']
        if Dt['𝜃A2'] is None:
            StrA += get_string('𝜃', Dt['𝜃A1'])
        else:
            StrA += '(' + get_string('𝜃', Dt['𝜃A1']) + '-' + \
                get_string('𝜃', Dt['𝜃A2']) + ')'

    StrB = ''
    if Dt['𝜃B1'] is not None:
        StrB = Dt['scB']
        if Dt['𝜃B2'] is None:
            StrB += get_string('𝜃', Dt['𝜃B1'])
        else:
            StrB += '(' + get_string('𝜃', Dt['𝜃B1']) + '-' + \
                get_string('𝜃', Dt['𝜃B2']) + ')'

    if Dt['val2'] is None:
        print('%.4f%s' % (Dt['val1'], Str+StrA), end='')
    else:
        if Dt['val3'] > 0:
            aux = '+'
        else:
            aux = ''
        print('%.4f%s[%.4f%s%s%.4f%s]' % (Dt['val1'], Str, Dt['val2'], StrA,
                                          aux, Dt['val3'], StrB), end='')


def develop_ΔPQ_V(Dt, V, flg):
    ''' Differential of P/Q with respect to V'''
    if V != Dt['V1'] and V != Dt['V2']:
        return flg

    Str = ''
    Val = 1
    if Dt['V1'] is not None:
        if V != Dt['V1']:
            Str += get_string('V', Dt['V1'])
    if Dt['V2'] is not None:
        if Dt['V1'] == Dt['V2']:
            Val = 2
        elif V != Dt['V2']:
            Str += get_string('V', Dt['V2'])

    StrA = ''
    if Dt['𝜃A1'] is not None:
        StrA = Dt['scA']
        if Dt['𝜃A2'] is None:
            StrA += get_string('𝜃', Dt['𝜃A1'])
        else:
            StrA += '(' + get_string('𝜃', Dt['𝜃A1']) + '-' + \
                get_string('𝜃', Dt['𝜃A2']) + ')'

    StrB = ''
    if Dt['𝜃B1'] is not None:
        StrA = Dt['scB']
        if Dt['𝜃B2'] is None:
            StrB += get_string('𝜃', Dt['𝜃B1'])
        else:
            StrB += '(' + get_string('𝜃', Dt['𝜃B1']) + '-' + \
                get_string('𝜃', Dt['𝜃B2']) + ')'

    if Dt['val1']*Val > 0 and flg:
        print(' + ', end='')

    if Dt['val2'] is None:
        print('%.4f%s' % (Dt['val1']*Val, Str+StrA), end='')
    else:
        if Dt['val3'] > 0:
            aux = '+'
        else:
            aux = ''
        print('%.4f%s[%.4f%s%s%.4f%s]' % (Dt['val1']*Val, Str, Dt['val2'],
                                          StrA, aux, Dt['val3'], StrB), end='')

    return True


def develop_ΔPQ_𝜃(Dt, 𝜃, flg):
    ''' String for differential of P/Q with respect to 𝜃'''
    if 𝜃 != Dt['𝜃A1'] and 𝜃 != Dt['𝜃A2'] and 𝜃 != Dt['𝜃B1'] and 𝜃 != Dt['𝜃B2']:
        return flg

    Str = ''
    if Dt['V1'] is not None:
        Str += get_string('V', Dt['V1'])
    if Dt['V2'] is not None:
        if Dt['V1'] == Dt['V2']:
            Str += '\u00b2'
        else:
            Str += get_string('V', Dt['V2'])

    StrA, ValA = diff_sin_cos(Dt['scA'], Dt['𝜃A1'], Dt['𝜃A2'], 𝜃)

    StrB, ValB = diff_sin_cos(Dt['scB'], Dt['𝜃B1'], Dt['𝜃B2'], 𝜃)

    if Dt['val2'] is None:
        if Dt['val1']*ValA > 0 and flg:
            print(' + ', end='')

        print('%.4f%s' % (Dt['val1']*ValA, Str+StrA), end='')
    else:
        if Dt['val1'] > 0 and flg:
            print(' + ', end='')
        if Dt['val3'] > 0:
            aux = '+'
        else:
            aux = ''
        print('%.4f%s[%.4f%s%s%.4f%s]'
              % (Dt['val1'], Str, Dt['val2']*ValA, StrA, aux, Dt['val3']*ValB,
                 StrB), end='')
    return True


def diff_sin_cos(Dt_sc, Dt_𝜃1, Dt_𝜃2, 𝜃):
    '''Developing the differentials of sine and cosine'''
    Str = ''
    Val = 1
    if Dt_𝜃1 is not None:
        if Dt_sc == 'sin':
            Str = 'cos'
        if Dt_sc == 'cos':
            Str = 'sin'
            Val = -1
        if Dt_𝜃2 is None:
            Str += get_string('𝜃', Dt_𝜃1)
        else:
            Str += '(' + get_string('𝜃', Dt_𝜃1) + '-' + \
                get_string('𝜃', Dt_𝜃2) + ')'
            if 𝜃 == Dt_𝜃2:
                Val *= -1

    return Str, Val


def get_diff_sin_cos(Dt_sc, Dt_𝜃1, Dt_𝜃2, 𝜃_All, 𝜃):
    if 𝜃 != Dt_𝜃1 and 𝜃 != Dt_𝜃2:
        return 0

    Val = 1
    if Dt_𝜃1 is not None:
        Ang = 𝜃_All[Dt_𝜃1]
    else:
        Ang = 0
    if Dt_𝜃2 is not None:
        Ang -= 𝜃_All[Dt_𝜃2]
        if 𝜃 == Dt_𝜃2:
            Val = -1

    if Dt_sc == 'sin':
        Val *= math.cos(Ang)
    else:
        Val *= -1*math.sin(Ang)

    return Val


def get_Imp_Unk(Bus_Type, Generator):
    ''' Get implicit equations and unknown variables '''
    Number_Buses = len(Bus_Type)
    V_All = [1 for bus in range(Number_Buses)]
    𝜃_All = [0 for bus in range(Number_Buses)]
    for gen in Generator:
        if 'V' in gen.keys():
            bus = gen['Bus']-1
            V_All[bus] = gen['V']
        if '𝜃' in gen.keys():
            bus = gen['Bus']-1
            𝜃_All[bus] = gen['𝜃']

    J_P = []  # Known P
    J_Q = []  # Known Q
    J_V = []  # Unknown V
    J_𝜃 = []  # Unknown 𝜃
    for bus in range(Number_Buses):
        if Bus_Type[bus] == 1:  # PQ
            J_P.append(bus)
            J_Q.append(bus)
            J_V.append(bus)
            J_𝜃.append(bus)
        if Bus_Type[bus] == 2:  # PV
            J_P.append(bus)
            J_𝜃.append(bus)
            V_All[bus]

    return J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All


def get_J_V(Dt_Raw, V_All, 𝜃_All, V):
    Dta = Dt_Raw[0]
    # PQ = Dt_Raw[1]
    # bus = Dt_Raw[2]
    # txt = Dt_Raw[3]

    Val = 0
    for part in range(len(Dta)):
        Dt = Dta[part]

        if Dt['V1'] == V or Dt['V2'] == V:

            aux = 1
            if Dt['V1'] is not None:
                if Dt['V1'] != V:
                    aux *= V_All[Dt['V1']]
                elif Dt['V1'] == Dt['V2']:
                    aux *= 2*V_All[Dt['V1']]

            if Dt['val2'] is None:
                Val += aux*Dt['val1']*get_sin_cos(Dt['scA'], Dt['𝜃A1'],
                                                  Dt['𝜃A2'], 𝜃_All)
            else:
                Val += aux*Dt['val1'] * \
                    (Dt['val2']*get_sin_cos(Dt['scA'], Dt['𝜃A1'], Dt['𝜃A2'],
                                            𝜃_All) +
                     Dt['val3']*get_sin_cos(Dt['scB'], Dt['𝜃B1'], Dt['𝜃B2'],
                                            𝜃_All))

    return Val


def get_J_𝜃(Dt_Raw, V_All, 𝜃_All, 𝜃):
    Dta = Dt_Raw[0]
    # PQ = Dt_Raw[1]
    # bus = Dt_Raw[2]
    # txt = Dt_Raw[3]

    Val = 0
    for part in range(len(Dta)):
        Dt = Dta[part]

        aux = 1
        if Dt['V1'] is not None:
            aux *= V_All[Dt['V1']]
        if Dt['V2'] is not None:
            aux *= V_All[Dt['V2']]

        if Dt['scB'] is None:
            Val += aux*Dt['val1']*get_diff_sin_cos(Dt['scA'], Dt['𝜃A1'],
                                                   Dt['𝜃A2'], 𝜃_All, 𝜃)
        else:
            Val += aux*Dt['val1'] * \
                (Dt['val2']*get_diff_sin_cos(Dt['scA'], Dt['𝜃A1'], Dt['𝜃A2'],
                                             𝜃_All, 𝜃) +
                 Dt['val3']*get_diff_sin_cos(Dt['scB'], Dt['𝜃B1'], Dt['𝜃B2'],
                                             𝜃_All, 𝜃))

    return Val


def get_Jacobian(P_Data, Q_Data, J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All):
    Number_J = len(J_V) + len(J_𝜃)
    J = numpy.zeros((Number_J, Number_J))

    i = 0
    for bus in J_P:
        j = 0
        for 𝜃 in J_𝜃:
            J[i][j] = get_J_𝜃(P_Data[bus], V_All, 𝜃_All, 𝜃)
            j += 1
        for V in J_V:
            J[i][j] = get_J_V(P_Data[bus], V_All, 𝜃_All, V)
            j += 1
        i += 1

    for bus in J_Q:
        j = 0
        for 𝜃 in J_𝜃:
            J[i][j] = get_J_𝜃(Q_Data[bus], V_All, 𝜃_All, 𝜃)
            j += 1
        for V in J_V:
            J[i][j] = get_J_V(Q_Data[bus], V_All, 𝜃_All, V)
            j += 1
        i += 1

    return J


def get_Parameters(Connectivity, V_All, 𝜃_All, Succes):
    ''' Calculate additional parameters '''
    if not Succes:
        return

    Base = 100
    Number_Buses = len(V_All)

    Results = {}
    Results['Connectivity'] = Connectivity
    Results['Voltage'] = []
    Results['Current'] = []
    Results['Sending_Power'] = []
    Results['Receiving_Power'] = []
    Results['Net_Power'] = [0 for bus in range(Number_Buses)]
    Results['Loss'] = []

    # Get complex voltages
    for bus in range(Number_Buses):
        Results['Voltage'].append(V_All[bus]*complex(math.cos(𝜃_All[bus]),
                                                     math.sin(𝜃_All[bus])))

    for branch in Connectivity:
        s = branch[0]-1
        r = branch[1]-1
        Y = 1/branch[2]

        # Complex voltages
        Vs = Results['Voltage'][s]
        Vr = Results['Voltage'][r]

        # Complex current
        I = Y * (Vs - Vr)

        # Power at both ends of the line
        Ss = Vs*I.conjugate()*Base
        Sr = -Vr*I.conjugate()*Base

        # Store data
        Results['Current'].append(I)
        Results['Sending_Power'].append(Ss)
        Results['Receiving_Power'].append(Sr)
        Results['Loss'].append(Ss+Sr)
        Results['Net_Power'][s] += Ss
        Results['Net_Power'][r] += Sr

    return Results


def get_sin_cos(Dt_sc, Dt_𝜃1, Dt_𝜃2, 𝜃_All):
    if Dt_sc is None:
        return 1

    if Dt_𝜃1 is not None:
        Ang = 𝜃_All[Dt_𝜃1]
    else:
        Ang = 0
    if Dt_𝜃2 is not None:
        Ang -= 𝜃_All[Dt_𝜃2]

    if Dt_sc == 'sin':
        Val = math.sin(Ang)
    else:
        Val = math.cos(Ang)

    return Val


def get_string(txt, bus1, bus2=None):
    '''Create string with subscripts'''
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    str1 = str(bus1+1).translate(SUB)
    if bus2 is None:
        str2 = ''
    else:
        str2 = ',' + str(bus2+1).translate(SUB)

    return txt+str1+str2


def get_Δ(Dt_Raw, V_All, 𝜃_All):
    Dta = Dt_Raw[0]
    PQ = Dt_Raw[1]
    # bus = Dt_Raw[2]
    # txt = Dt_Raw[3]

    Val = 0
    for part in range(len(Dta)):
        Dt = Dta[part]

        aux = 1
        if Dt['V1'] is not None:
            aux *= V_All[Dt['V1']]
        if Dt['V2'] is not None:
            aux *= V_All[Dt['V2']]

        if Dt['val2'] is None:
            Val += aux*Dt['val1']*get_sin_cos(Dt['scA'], Dt['𝜃A1'], Dt['𝜃A2'],
                                              𝜃_All)
        else:
            Val += aux*Dt['val1'] * \
                (Dt['val2']*get_sin_cos(Dt['scA'], Dt['𝜃A1'], Dt['𝜃A2'],
                                        𝜃_All) +
                 Dt['val3']*get_sin_cos(Dt['scB'], Dt['𝜃B1'], Dt['𝜃B2'],
                                        𝜃_All))
    Val -= PQ

    return Val


def get_ΔPQ(P_Data, Q_Data, J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All):
    Δ = []

    for bus in J_P:
        Δ.append(get_Δ(P_Data[bus], V_All, 𝜃_All))

    for bus in J_Q:
        Δ.append(get_Δ(Q_Data[bus], V_All, 𝜃_All))

    return Δ


def Newtons_Method(P_Data, Q_Data, Bus_Data, Bus_Type, Generator, Disp_Iter=1):
    J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All = get_Imp_Unk(Bus_Type, Generator)

    iterations = 0
    flg = True
    while flg:
        Δ = get_ΔPQ(P_Data, Q_Data, J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All)
        J = get_Jacobian(P_Data, Q_Data, J_P, J_Q, J_V, J_𝜃, V_All, 𝜃_All)
        V_All, 𝜃_All, dx, Threshold = update_Unknowns(J, Δ, J_𝜃, J_V, 𝜃_All,
                                                      V_All)

        iterations += 1
        if iterations <= Disp_Iter:
            print('ITERATION:', iterations)
            print('Vector of mismatches:', Δ)
            print('Jacobian:\n', J)
            print('dx', dx)
            print('Updated voltage magnitudes [pu]: ', V_All)
            print('Updated voltage angles    [rad]: ', 𝜃_All)
            print()

        if iterations > 20:
            print('The model failed to converge after 20 iterations')
            flg = False
            Succes = False
        if Threshold < 0.0001:
            flg = False
            Succes = True
    if Disp_Iter > 0:
        print('RESULTS:')
        print('V:', V_All, '(pu)')
        print('𝜃:', 𝜃_All, '(rad)')
        print()

    return V_All, 𝜃_All, Threshold, Succes


def update_Unknowns(J, Δ, J_𝜃, J_V, 𝜃_All, V_All):
    import numpy
    dx = numpy.linalg.inv(J).dot(Δ)
    Threshold = max(abs(dx))

    j = 0
    for 𝜃 in J_𝜃:
        𝜃_All[𝜃] -= dx[j]
        j += 1
    for V in J_V:
        V_All[V] -= dx[j]
        j += 1
    return V_All, 𝜃_All, dx, Threshold


def Visualize_Elec(Connectivity, V_All, 𝜃_All, Succes):
    Results = get_Parameters(Connectivity, V_All, 𝜃_All, Succes)
    if not Succes:
        return

    # Number_Buses = len(V_All)
    print('VOLTAGES  [pu] [deg]:')
    xn = 0
    for V in Results['Voltage']:
        xn += 1
        print('%2.0f) %8.4f +j %8.4f (%8.4f ∠ %8.4f)'
              % (xn, V.real, V.imag, abs(V), cmath.phase(V)*180/math.pi))

    print('NET POWER INJECTIONS [MVA]:')
    xn = 0
    for S in Results['Net_Power']:
        xn += 1
        print('%2.0f) %8.4f +j %8.4f' % (xn, S.real, S.imag))

    print('CURRENTS [pu] [deg]:')
    xb = 0
    for branch in Results['Connectivity']:
        s = branch[0]
        r = branch[1]
        I = Results['Current'][xb]
        xb += 1
        print('%2.0f-%2.0f) %8.4f +j %8.4f (%8.4f ∠ %8.4f)'
              % (s, r, I.real, I.imag, abs(I), cmath.phase(I)*180/math.pi))

    print('POWER FLOWS [MVA]:')
    print('      From:                To:                   Loss:')
    xb = 0
    for branch in Results['Connectivity']:
        s = branch[0]
        r = branch[1]
        Ss = Results['Sending_Power'][xb]
        Sr = Results['Receiving_Power'][xb]
        xb += 1
        print('%2.0f-%2.0f) %8.4f +j %8.4f %8.4f +j %8.4f (%8.4f +j %8.4f)'
              % (s, r, Ss.real, Ss.imag, Sr.real, Sr.imag, Ss.real+Sr.real,
                 Ss.imag+Sr.imag))
