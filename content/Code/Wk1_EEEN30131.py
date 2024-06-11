# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""

import numpy


def get_Ybus(Connectivity, flg=False, prnt=True):

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
        print('The network has %d branches and %d buses' % (Number_Branches,
                                                            Number_Buses))
        print('______________________________')
        print('Branch | From - To | Impedance')
        print('------------------------------')
        for branch in range(Number_Branches):
            print('%5.0f  | %4.0f - %2.0f |' % (branch+1,
                                                Connectivity[branch][0],
                                                Connectivity[branch][1]),
                  end=' ')
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
    # Get number of branches
    Number_Branches = len(Connectivity)

    # Get number of nodes
    Number_Buses = 0
    for branch in range(Number_Branches):
        Number_Buses = \
            max([Number_Buses, Connectivity[branch][0],
                 Connectivity[branch][1]])

    # Display network data
    print('The network has %d branches and %d buses' % (Number_Branches,
                                                        Number_Buses))
    print('______________________________')
    print('Branch | From - To | Impedance')
    print('------------------------------')
    for branch in range(Number_Branches):
        print('%5.0f  | %4.0f - %2.0f |' % (branch+1, Connectivity[branch][0],
                                            Connectivity[branch][1]), end=' ')
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

        print('\nChecking branch %d (%d-%d)' % (branch+1, F, T), end=' ')
        print('with an impedance of', Z, ' (admittance of', Y, ')')

        if From >= 0 and To >= 0:
            print('The value of the off-diagonal elements ', end='')
            print('(%d,%d) and (%d,%d) is:'
                  % (F, T, T, F), -Y)
            Ybus[From][To] = -Y
            Ybus[To][From] = -Y

        if From >= 0:
            print('The value of the diagonal element (%d,%d)' %
                  (F, F), ' changes from ', Ybus[From][From], end=' ')
            Ybus[From][From] += Y
            print('to', Ybus[From][From])

        if To >= 0:
            print('The value of the diagonal element (%d,%d)' %
                  (T, T), ' changes from ', Ybus[To][To], end=' ')
            Ybus[To][To] += Y
            print('to', Ybus[To][To])

    print('\nYbus = \n', Ybus)
    if flg:
        return Ybus
