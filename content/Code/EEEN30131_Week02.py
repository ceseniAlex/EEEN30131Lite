# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""


class Object(object):
    pass


class Week_01:
    '''Default settings used for week 01'''

    def __init__(self):
        self.data = Object()

    def get_Ybus(Connectivity, flg=False, prnt=True):
        import numpy

        # Get number of branches
        Number_Branches = len(Connectivity)

        # Get number of nodes
        Number_Buses = 0
        for branch in range(Number_Branches):
            Number_Buses = \
                max([Number_Buses, Connectivity[branch][0],
                     Connectivity[branch][1]])

        # Display network data
        if prnt:
            print('The network has %d branches and %d buses'%(Number_Branches, Number_Buses))
            print('______________________________')
            print('Branch | From - To | Impedance')
            print('------------------------------')
            for branch in range(Number_Branches):
                print('%5.0f  | %4.0f - %2.0f |'%(branch+1, Connectivity[branch][0], Connectivity[branch][1]), end=' ')
                print(Connectivity[branch][2])
            print('_______|___________|__________')

        # Build Ybus matrix
        Ybus = numpy.zeros((Number_Buses, Number_Buses), dtype=complex)
        for branch in range(Number_Branches):
            From = Connectivity[branch][0] - 1
            To = Connectivity[branch][1] - 1

            Y = 1/Connectivity[branch][2]

            if From >= 0 and To >= 0:
                Ybus[From][To] = -Y
                Ybus[To][From] = -Y

            if From >= 0:
                Ybus[From][From] += Y

            if To >= 0:
                Ybus[To][To] += Y

        if prnt:
            print('\nYbus = \n', Ybus)
        if flg:
            return Ybus

    def get_Ybus_Steps(Connectivity, flg=False):
        import numpy

        # Get number of branches
        Number_Branches = len(Connectivity)

        # Get number of nodes
        Number_Buses = 0
        for branch in range(Number_Branches):
            Number_Buses = \
                max([Number_Buses, Connectivity[branch][0],
                     Connectivity[branch][1]])

        # Display network data
        print('The network has %d branches and %d buses'%(Number_Branches, Number_Buses))
        print('______________________________')
        print('Branch | From - To | Impedance')
        print('------------------------------')
        for branch in range(Number_Branches):
            print('%5.0f  | %4.0f - %2.0f |'%(branch+1, Connectivity[branch][0], Connectivity[branch][1]), end=' ')
            print(Connectivity[branch][2])
        print('_______|___________|__________')

        print('\nBUILDING ADMITTANCE MATRIX:')
        Ybus = numpy.zeros((Number_Buses, Number_Buses), dtype=complex)
        for branch in range(Number_Branches):
            F = Connectivity[branch][0]
            T = Connectivity[branch][1]
            From = F - 1
            To = T - 1

            Z = Connectivity[branch][2]
            Y = 1/Z

            print('\nChecking branch %d (%d-%d)'%(branch+1, F, T), end=' ')
            print('with an impedance of', Z,' (admittance of', Y,')')

            if From >= 0 and To >= 0:
                print('The value of the off-diagonal elements (%d,%d) and (%d,%d) is:'
                      % (F, T, T, F), -Y)
                Ybus[From][To] = -Y
                Ybus[To][From] = -Y

            if From >= 0:
                print('The value of the diagonal element (%d,%d)'%
                     (F,F),' changes from ', Ybus[From][From], end=' ')
                Ybus[From][From] += Y
                print('to', Ybus[From][From])
    
            if To >= 0:
                print('The value of the diagonal element (%d,%d)'%
                      (T, T),' changes from ', Ybus[To][To], end=' ')
                Ybus[To][To] += Y
                print('to', Ybus[To][To])

        print('\nYbus = \n', Ybus)
        if flg:
            return Ybus


class Week_02:
    '''Default settings used for week 01'''

    def __init__(self):
        self.data = Object()

    def get_Bus_Data(Load, Generator, Ybus):
        Number_Buses = len(Ybus)
        Bus_Data = [{'V':None, '𝜃':None, 'P':0, 'Q':0} for bus in range(Number_Buses)]

        for load in Load:  # Load can inject active and reactive power
            bus = load[0]-1
            Bus_Data[bus]['P'] -= load[1].real
            Bus_Data[bus]['Q'] -= load[1].imag

        for gen in Generator:  # Generators are a bit more complicated
            if len(gen.keys()) != 3:
                print('Invalid generation data:', gen)
                break
            bus = gen['Bus'] - 1
            if 'P' in gen.keys() and 'Q' in gen.keys():  # Some generators may inject active and reactive power
                Bus_Data[bus]['P'] += gen['P']
                Bus_Data[bus]['Q'] += gen['Q']
            elif 'P' in gen.keys() and 'V' in gen.keys():  # Others control voltages
                if Bus_Data[bus]['V'] != None:
                    print('There should not be two generators defining the voltage of bus ', gen['Bus'])
                Bus_Data[bus]['P'] += gen['P']
                Bus_Data[bus]['V'] = gen['V']
            elif 'V' in gen.keys() and '𝜃' in gen.keys():  # Others can act as the slack generator
                if Bus_Data[bus]['V'] != None:
                    print('There should not be two generators defining the voltage of bus ', gen['Bus'])
                if Bus_Data[bus]['𝜃'] != None:
                    print('There should not be two generators defining the angle of bus ', gen['Bus'])
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
            if Bus_Data[bus]['𝜃'] != None:
                Bus_Type.append(3)
                Bus_Data[bus].pop('P')
                Bus_Data[bus].pop('Q')
    
                # If its not the slack and we know V, it has to be a PV bus
            elif Bus_Data[bus]['V'] != None:
                Bus_Type.append(2)
                Bus_Data[bus].pop('Q')
                Bus_Data[bus].pop('𝜃')
    
                # ALl we have left is PQ buses
            else:
                Bus_Type.append(1)
                Bus_Data[bus].pop('V')
                Bus_Data[bus].pop('𝜃')
        return Bus_Data, Bus_Type

    def display_Bus_Type(Bus_Data, Bus_Type):
        print('Bus:  Type:       V:       𝜃:     Pinj:     Qinj:')
        for bus in range(len(Bus_Data)):
            print('%4.0f'%(bus+1), end='')
            if Bus_Type[bus] == 1:
                print('     PQ        ?        ?  %8.4f  %8.4f'
                      %(Bus_Data[bus]['P'], Bus_Data[bus]['Q']))
            elif Bus_Type[bus] == 2:
                print('     PV %8.4f        ?  %8.4f         ?'
                      %(Bus_Data[bus]['V'], Bus_Data[bus]['P']))
            else:
                print('  Slack %8.4f %8.4f         ?         ?'
                      %(Bus_Data[bus]['V'], Bus_Data[bus]['𝜃']))


class Week_03:
    '''Default settings used for week 01'''

    def __init__(self):
        self.data = Object()


class Week_04:
    '''Default settings used for week 01'''

    def __init__(self):
        self.data = Object()


class Week_05:
    '''Default settings used for week 01'''

    def __init__(self):
        self.data = Object()


class Week_06:
    '''Default settings used for week 01'''

    def __init__(self):
        self.data = Object()

