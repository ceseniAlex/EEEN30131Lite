# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""

import math


def develop_PF_Equations(Load, Generator, Ybus, flg=False, Prnt=True):
    Bus_Data, Bus_Type = get_Bus_Type(Ybus, Load, Generator)
    if Prnt:
        print()
        display_Bus_Type(Bus_Data, Bus_Type)
    if Prnt:
        print()
        print('***DEVELOP AND SIMPLIFY***')
    Number_Buses = len(Ybus)

    P_Data = []
    for bus in range(Number_Buses):
        if Prnt:
            print('P%d:' % (bus+1))
            develop_PQ_V01('P', bus, Ybus, Bus_Data)
        Gflag, Bflag = develop_PQ_V02('P', bus, Ybus, Bus_Data, Prnt)
        Gflag, Bflag, Nxt = develop_PQ_V03('P', bus, Ybus, Bus_Data, Gflag,
                                           Bflag, Prnt)
        if Prnt:
            develop_PQ_V04('P', bus, Ybus, Bus_Data, Gflag, Bflag, Nxt)
        P_Dt = develop_PQ_V05('P', bus, Ybus, Bus_Data, Gflag, Bflag, Nxt, flg,
                              Prnt)
        P_Data.append(P_Dt)
        if Prnt:
            print()

    Q_Data = []
    for bus in range(Number_Buses):
        if Prnt:
            print('Q%d:' % (bus+1))
            develop_PQ_V01('Q', bus, Ybus, Bus_Data)
        Gflag, Bflag = develop_PQ_V02('Q', bus, Ybus, Bus_Data, Prnt)
        Gflag, Bflag, Nxt = develop_PQ_V03('Q', bus, Ybus, Bus_Data, Gflag,
                                           Bflag, Prnt)
        if Prnt:
            develop_PQ_V04('Q', bus, Ybus, Bus_Data, Gflag, Bflag, Nxt)
        Q_Dt = develop_PQ_V05('Q', bus, Ybus, Bus_Data, Gflag, Bflag, Nxt, flg,
                              Prnt)
        Q_Data.append(Q_Dt)
        if Prnt:
            print()

    if flg:
        return P_Data, Q_Data


def develop_PQ_V01(txt, bus1, Ybus, Bus_Data, Prnt=True):

    PQ = get_string(txt, bus1)
    print('%s = ' % PQ, end='')

    V1 = get_string('V', bus1)

    Number_Buses = len(Ybus)
    for bus2 in range(Number_Buses):

        V2 = get_string('V', bus2)
        𝜃12 = get_string('𝜃', bus1, bus2)
        G12 = get_string('G', bus1, bus2)
        B12 = get_string('B', bus1, bus2)

        sc1, _ = get_P_Q(txt, 1)
        sgn, _ = get_P_Q(txt, 2)
        sc2, _ = get_P_Q(txt, 3)

        if Prnt:
            print('%s%s[%s%s%s%s%s%s%s]'
                  % (V1, V2, G12, sc1, 𝜃12, sgn, B12, sc2, 𝜃12), end=' ')
            if bus2 < Number_Buses-1:
                print('+ ', end='')
            else:
                print()


def develop_PQ_V02(txt, bus1, Ybus, Bus_Data, Prnt=True):

    PQ = get_string(txt, bus1)
    if Prnt:
        print('%s = ' % PQ, end='')

    V1 = get_string('V', bus1)

    Gflag = []
    Bflag = []
    flg = False
    for bus2 in range(len(Ybus)):

        # Is G greater than zero?
        if abs(Ybus[bus1][bus2].real) > 0.0001:
            flgg = True
        else:
            flgg = False
        Gflag.append(flgg)

        # Is B is greater than zero zero?
        if abs(Ybus[bus1][bus2].imag) > 0.0001:
            flgb = True
        else:
            flgb = False
        Bflag.append(flgb)

        if flgg or flgb:
            if flg and Prnt:
                print(' + ', end='')
            flg = True
            V2 = get_string('V', bus2)
            𝜃12 = get_string('𝜃', bus1, bus2)
            if Prnt:
                print('%s*%s*' % (V1, V2), end='')

        if flgg and flgb and Prnt:
            print('[', end='')

        if flgg:
            G12 = get_string('G', bus1, bus2)
            sc1, _ = get_P_Q(txt, 1)
            if Prnt:
                print('%s*%s%s' % (G12, sc1, 𝜃12), end='')

        if flgb:
            _, sgnv = get_P_Q(txt, 2)
            if sgnv < 0:
                if Prnt:
                    print('-', end='')
            else:
                if flgg:
                    if Prnt:
                        print('+', end='')
            B12 = get_string('B', bus1, bus2)
            sc2, _ = get_P_Q(txt, 3)
            if Prnt:
                print('%s*%s%s' % (B12, sc2, 𝜃12), end='')

        if flgg and flgb and Prnt:
            print(']', end='')
    if Prnt:
        print()

    return Gflag, Bflag


def develop_PQ_V03(txt, bus1, Ybus, Bus_Data, Gflg, Bflg, Prnt=True):

    PQ = get_string(txt, bus1)
    if Prnt:
        print('%s = ' % PQ, end='')

    V1 = get_string('V', bus1)

    Gflag = []
    Bflag = []
    flg = False
    Nxt = [False for x in range(len(Ybus))]
    for bus2 in range(len(Ybus)):

        # Is the first component non-zero?
        flgg = False
        if Gflg[bus2]:
            sc1, scv1 = get_P_Q(txt, 1)
            if bus1 == bus2:
                if scv1 != 0:
                    flgg = True
            else:
                flgg = True
        Gflag.append(flgg)

        # Is the second component non-zero?
        flgb = False
        if Bflg[bus2]:
            sc2, scv2 = get_P_Q(txt, 3)
            if bus1 == bus2:
                if scv2 != 0:
                    flgb = True
            else:
                flgb = True
        Bflag.append(flgb)

        if flgg or flgb:
            if flg and Prnt:
                Nxt[bus2] = True
                print(' + ', end='')
            flg = True
            if bus1 == bus2:
                if Prnt:
                    print('%s\u00b2*' % V1, end='')
            else:
                V2 = get_string('V', bus2)
                𝜃12 = get_string('𝜃', bus1, bus2)
                if Prnt:
                    print('%s*%s*' % (V1, V2), end='')

        if flgg and flgb and Prnt:
            print('[', end='')

        if flgg:
            G12 = get_string('G', bus1, bus2)
            𝜃12 = get_string('𝜃', bus1, bus2)
            if Prnt:
                print('%s*%s%s' % (G12, sc1, 𝜃12), end='')

        if flgb:
            _, sgnv = get_P_Q(txt, 2)
            if sgnv < 0:
                if Prnt:
                    print('-', end='')
            else:
                if flgg and Prnt:
                    print('+', end='')
            B12 = get_string('B', bus1, bus2)
            if Prnt:
                if bus1 == bus2:
                    print('%s' % B12, end='')
                else:
                    print('%s*%s%s' % (B12, sc2, 𝜃12), end='')

        if flgg and flgb and Prnt:
            print(']', end='')

    if Prnt:
        print()

    return Gflag, Bflag, Nxt


def develop_PQ_V04(txt, bus1, Ybus, Bus_Data, Gflg, Bflg, Nxt):

    PQ, _, _, _ = get_Bus_Value(Bus_Data, txt, bus1)
    print('%s = ' % PQ, end='')

    V1, _, _, _ = get_Bus_Value(Bus_Data, 'V', bus1)
    𝜃1, _, _, _ = get_Bus_Value(Bus_Data, '𝜃', bus1)

    for bus2 in range(len(Ybus)):
        flgg = Gflg[bus2]
        flgb = Bflg[bus2]

        if flgg or flgb:
            if Nxt[bus2]:
                print(' + ', end='')

            if bus1 == bus2:
                print('%s\u00b2*' % V1, end='')
            else:
                V2, _, _, _ = get_Bus_Value(Bus_Data, 'V', bus2)
                𝜃2, _, _, _ = get_Bus_Value(Bus_Data, '𝜃', bus2)
                print('%s*%s*' % (V1, V2), end='')

        if flgg and flgb:
            print('[', end='')

        if flgg:
            G12 = str(Ybus[bus1][bus2].real)
            𝜃2, _, _, _ = get_Bus_Value(Bus_Data, '𝜃', bus2)
            sc1, _ = get_P_Q(txt, 1)
            print('%s*%s(%s-%s)' % (G12, sc1, 𝜃1, 𝜃2), end='')

        if flgb:
            _, sgnv = get_P_Q(txt, 2)
            if sgnv < 0:
                print('-', end='')
            else:
                if flgg:
                    print('+', end='')
            B12 = str(Ybus[bus1][bus2].imag)
            if bus1 == bus2:
                print('%s' % B12, end='')
            else:
                sc2, _ = get_P_Q(txt, 3)
                print('%s*%s(%s-%s)' % (B12, sc2, 𝜃1, 𝜃2), end='')

        if flgg and flgb:
            print(']', end='')

    print()


def develop_PQ_V05(txt, bus1, Ybus, Bus_Data, Gflg, Bflg, Nxt, flg=False,
                   Prnt=True):

    PQ, _, PQv, PQf = get_Bus_Value(Bus_Data, txt, bus1)
    if Prnt:
        print('%s = ' % PQ, end='')
    if PQf:
        Delta_Data = PQv
    else:
        Delta_Data = None

    _, Vs1, Vv1, Vf1 = get_Bus_Value(Bus_Data, 'V', bus1)
    𝜃1, 𝜃s1, 𝜃v1, 𝜃f1 = get_Bus_Value(Bus_Data, '𝜃', bus1)

    PQ_Data = []
    for bus2 in range(len(Ybus)):
        PQ_Dt = {'V1': None, 'V2': None,
                 'scA': None, '𝜃A1': None, '𝜃A2': None,
                 'scB': None, '𝜃B1': None, '𝜃B2': None,
                 'val1': None, 'val2': None, 'val3': None}

        flgg = Gflg[bus2]
        flgb = Bflg[bus2]

        _, Vs2, Vv2, Vf2 = get_Bus_Value(Bus_Data, 'V', bus2)
        𝜃2, 𝜃s2, 𝜃v2, 𝜃f2 = get_Bus_Value(Bus_Data, '𝜃', bus2)

        if bus1 == bus2 and Vs1 != '':
            Vs12 = Vs1 + '\u00b2'
        else:
            Vs12 = Vs1+Vs2

        scv1, scs1, sc1 = develop_𝜃(txt, Bus_Data, 1, bus1, bus2, 𝜃s1, 𝜃v1,
                                    𝜃f1, 𝜃s2, 𝜃v2, 𝜃f2)
        scv2, scs2, sc2 = develop_𝜃(txt, Bus_Data, 3, bus1, bus2, 𝜃s1, 𝜃v1,
                                    𝜃f1, 𝜃s2, 𝜃v2, 𝜃f2)

        _, sgnv = get_P_Q(txt, 2)

        # Should both G and B components be considered?
        if flgg and flgb:
            if Nxt[bus2] and Prnt:
                print(' + ', end='')
            PQ_Dt['val1'] = Vv1*Vv2
            if Prnt:
                print('%.4f%s[' % (PQ_Dt['val1'], Vs12), end='')

            PQ_Dt['val2'] = scv1*Ybus[bus1][bus2].real
            PQ_Dt['scA'] = sc1
            if Prnt:
                print('%.4f%s' % (PQ_Dt['val2'], scs1), end='')

            PQ_Dt['val3'] = sgnv*scv2*Ybus[bus1][bus2].imag
            if PQ_Dt['val3'] > 0 and Prnt:
                print('+', end='')

            PQ_Dt['scB'] = sc2
            if Prnt:
                print('%.4f%s' % (PQ_Dt['val3'], scs2), end='')
                print(']', end='')

        elif flgg:  # Should only G be considered?
            PQ_Dt['val1'] = Vv1*Vv2*scv1*Ybus[bus1][bus2].real
            if Nxt[bus2] and Nxt[bus2] > 0 and Prnt:
                print(' + ', end='')
            PQ_Dt['scA'] = sc1
            if Prnt:
                print('%.4f%s' % (PQ_Dt['val1'], Vs12+scs1), end='')

        elif flgb:  # Should only B be considered
            PQ_Dt['val1'] = Vv1*Vv2*scv2*sgnv*Ybus[bus1][bus2].imag
            if Nxt[bus2] and PQ_Dt['val1'] > 0 and Prnt:
                print(' + ', end='')
            PQ_Dt['scA'] = sc2
            if Prnt:
                print('%.4f%s' % (PQ_Dt['val1'], Vs12+scs2), end='')

        if flgg or flgb:
            if not Vf1:
                PQ_Dt['V1'] = bus1
                if not Vf2:
                    PQ_Dt['V2'] = bus2
            else:
                if not Vf2:
                    PQ_Dt['V1'] = bus2

            aux = '𝜃A'
            if flgg and scs1 != '':
                if not 𝜃f1:
                    PQ_Dt['𝜃A1'] = bus1
                    aux = '𝜃B'
                    if not 𝜃f2:
                        PQ_Dt['𝜃A2'] = bus2
                else:
                    if not 𝜃f2:
                        PQ_Dt['𝜃A1'] = bus2
                        aux = '𝜃B'

            if flgb and scs2 != '':
                if not 𝜃f1:
                    PQ_Dt[aux+'1'] = bus1
                    if not 𝜃f2:
                        PQ_Dt[aux+'2'] = bus2
                else:
                    if not 𝜃f2:
                        PQ_Dt[aux+'1'] = bus2

            PQ_Data.append(PQ_Dt)
    if Prnt:
        if PQf:
            print('.....[Implicit]')
        else:
            print('.....[Explicit]')

    if flg:
        return (PQ_Data, Delta_Data, bus1, txt)


def develop_𝜃(txt, Bus_Data, No, bus1, bus2, 𝜃s1, 𝜃v1, 𝜃f1, 𝜃s2, 𝜃v2, 𝜃f2):
    if bus1 == bus2:
        _, Val = get_P_Q(txt, No, 0)
        Str1 = ''
        Str = None
    elif 𝜃f1 and 𝜃f2:
        _, Val = get_P_Q(txt, No, 𝜃v1-𝜃v2)
        Str1 = ''
        Str = None
    elif 𝜃f1:
        Str, Val = get_P_Q(txt, No, -1)
        if 𝜃v1 == 0:
            if Val < 0:
                Val = -1
            else:
                Val = 1
            Str1 = Str + '(' + 𝜃s2 + ')'
        else:
            Str1 = Str + '(' + str(𝜃v1) + '-' + 𝜃s2 + ')'
    elif 𝜃f2:
        Str, _ = get_P_Q(txt, No)
        Val = 1
        if 𝜃v2 == 0:
            Str1 = Str + '(' + 𝜃s1 + ')'
        else:
            print('Part 2', 𝜃s2, 𝜃v2, 𝜃f2)
            Str1 = Str + '(' + 𝜃s1 + '-' + str(𝜃v2) + ')'
    else:
        Str, _ = get_P_Q(txt, No)
        Val = 1
        Str1 = Str + '(' + 𝜃s1 + '-' + 𝜃s2 + ')'

    return Val, Str1, Str


def display_Bus_Type(Bus_Data, Bus_Type):
    print('Bus:  Type:       V:       𝜃:     Pinj:     Qinj:')
    for bus in range(len(Bus_Data)):
        print('%4.0f' % (bus+1), end='')
        if Bus_Type[bus] == 1:
            print('     PQ        ?        ?  %8.4f  %8.4f'
                  % (Bus_Data[bus]['P'], Bus_Data[bus]['Q']))
        elif Bus_Type[bus] == 2:
            print('     PV %8.4f        ?  %8.4f         ?'
                  % (Bus_Data[bus]['V'], Bus_Data[bus]['P']))
        else:
            print('  Slack %8.4f %8.4f         ?         ?'
                  % (Bus_Data[bus]['V'], Bus_Data[bus]['𝜃']))


def get_Bus_Data(Load, Generator, Ybus):
    Number_Buses = len(Ybus)
    Bus_Data = [{'V': None, '𝜃': None, 'P': 0, 'Q': 0}
                for bus in range(Number_Buses)]

    for load in Load:  # Load can inject active and reactive power
        bus = load[0]-1
        Bus_Data[bus]['P'] -= load[1].real
        Bus_Data[bus]['Q'] -= load[1].imag

    for gen in Generator:  # Generators are a bit more complicated
        if len(gen.keys()) != 3:
            print('Invalid generation data:', gen)
            break
        bus = gen['Bus'] - 1
        # Some generators may inject active and reactive power
        if 'P' in gen.keys() and 'Q' in gen.keys():
            Bus_Data[bus]['P'] += gen['P']
            Bus_Data[bus]['Q'] += gen['Q']
            # Others control voltages
        elif 'P' in gen.keys() and 'V' in gen.keys():
            if Bus_Data[bus]['V'] is not None:
                print('There should only be one generator ', end='')
                print('defining the voltage of bus ', gen['Bus'])
            Bus_Data[bus]['P'] += gen['P']
            Bus_Data[bus]['V'] = gen['V']
            # Others can act as the slack generator
        elif 'V' in gen.keys() and '𝜃' in gen.keys():
            if Bus_Data[bus]['V'] is not None:
                print('There should only be one generator ', end='')
                print('defining the voltage of bus ', gen['Bus'])
            if Bus_Data[bus]['𝜃'] is not None:
                print('There should only be one generator ', end='')
                print('defining the angle of bus ', gen['Bus'])
            Bus_Data[bus]['V'] = gen['V']
            Bus_Data[bus]['𝜃'] = gen['𝜃']
        else:
            print('Invalid generation data:', gen)
            break
    return Bus_Data


def get_Bus_Type(Ybus, Load, Generator):
    Bus_Data = get_Bus_Data(Load, Generator, Ybus)
    Bus_Type = []
    Number_Buses = len(Ybus)

    for bus in range(Number_Buses):
        # If 𝜃 is known, it has to be a slack bus
        if Bus_Data[bus]['𝜃'] is not None:
            Bus_Type.append(3)
            Bus_Data[bus].pop('P')
            Bus_Data[bus].pop('Q')

            # If its not the slack and we know V, it has to be a PV bus
        elif Bus_Data[bus]['V'] is not None:
            Bus_Type.append(2)
            Bus_Data[bus].pop('Q')
            Bus_Data[bus].pop('𝜃')

            # ALl we have left is PQ buses
        else:
            Bus_Type.append(1)
            Bus_Data[bus].pop('V')
            Bus_Data[bus].pop('𝜃')
    return Bus_Data, Bus_Type


def get_Bus_Value(Bus_Data, txt, bus):
    '''Get known and unknown data'''

    # Is the data known?
    if txt in Bus_Data[bus].keys():
        Val = Bus_Data[bus][txt]  # Get value
        Str1 = str(Val)  # Get string (number of symbol)
        Str2 = ''  # Get string (number of empty)
        flg = True
    else:
        Str1 = get_string(txt, bus)  # Get string (number of symbol)
        Str2 = Str1  # Get string (number of empty)
        Val = 1
        flg = False

    return Str1, Str2, Val, flg


def get_P_Q(txt, No, val=0):
    if txt == 'P':
        if No == 1:
            Str = 'cos'
            Val = math.cos(val)
        elif No == 2:
            Str = '+'
            Val = 1
        elif No == 3:
            Str = 'sin'
            Val = math.sin(val)
    elif txt == 'Q':
        if No == 1:
            Str = 'sin'
            Val = math.sin(val)
        elif No == 2:
            Str = '-'
            Val = -1
        elif No == 3:
            Str = 'cos'
            Val = math.cos(val)

    return Str, Val


def get_string(txt, bus1, bus2=None):
    '''Create string with subscripts'''
    SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    str1 = str(bus1+1).translate(SUB)
    if bus2 is None:
        str2 = ''
    else:
        str2 = ',' + str(bus2+1).translate(SUB)

    return txt+str1+str2
