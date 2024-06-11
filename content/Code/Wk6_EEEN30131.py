# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 12:46:33 2024

@author: mchihem2
"""

import cmath
import numpy
import matplotlib.pyplot as plt
import math
from Code.Wk2_EEEN30131 import get_Bus_Type, develop_PF_Equations
from Code.Wk3_EEEN30131 import Newtons_Method


def bfs(Generator, Connectivity, Load):
    V1 = Generator[0]['V'] * \
        complex(math.cos(Generator[0]['𝜃']),
                math.sin(Generator[0]['𝜃']))
    V2 = complex(1, 0)
    Z = Connectivity[0][2]
    B = complex(0, Connectivity[0][3])
    S2 = -Load[0][1]

    Threshold = cmath.inf
    flg = True
    iterations = 0
    while flg:
        I = -(S2/V2).conjugate() + V2*B/2  # Backward sweep
        Threshold = abs(V2 - V1 + I * Z)  # Calculate error
        V2 = V1 - I * Z  # Forward sweep

        # Convergence criteria
        iterations += 1
        if iterations > 20:
            print('The model failed to converge after 20 iterations')
            flg = False
            Succes = False
        if Threshold < 0.00001:  # Accuracy check
            flg = False
            Succes = True

    V_All = [abs(V1), abs(V2)]
    𝜃_All = [cmath.phase(V1), cmath.phase(V2)]

    return V_All, 𝜃_All, Threshold, Succes


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
    Results['Current2'] = []
    Results['Sending_Power'] = []
    Results['Receiving_Power'] = []
    Results['Net_Power'] = [0 for bus in range(Number_Buses)]
    Results['Loss'] = []
    Results['Generation'] = []

    # Get complex voltages
    for bus in range(Number_Buses):
        Results['Voltage'].append(V_All[bus]*complex(math.cos(𝜃_All[bus]),
                                                     math.sin(𝜃_All[bus])))

    for branch in Connectivity:
        s = branch[0]-1
        r = branch[1]-1
        Y = 1/branch[2]
        B = complex(0, branch[3]/2)

        # Complex voltages
        Vs = Results['Voltage'][s]
        Vr = Results['Voltage'][r]

        # Complex currents
        I = Y * (Vs - Vr)
        I1 = Y * (Vs - Vr) + Vs*B
        I2 = Y * (Vr - Vs) + Vr*B

        # Power at both ends of the line
        Ss0 = Vs*I.conjugate()*Base
        Sr0 = Vr*I.conjugate()*Base
        Ss = Vs*I1.conjugate()*Base
        Sr = Vr*I2.conjugate()*Base

        # Store data
        Results['Current'].append(I1)
        Results['Current2'].append(I2)
        Results['Sending_Power'].append(Ss)
        Results['Receiving_Power'].append(Sr)
        Results['Loss'].append(Ss0-Sr0)
        Results['Net_Power'][s] += Ss
        Results['Net_Power'][r] += Sr

    return Results


def get_power_circle(V_All, Connectivity):
    '''Method to create power circle diagrams'''
    # Radius
    radius = abs(V_All[0]) * abs(V_All[1]) / abs(Connectivity[0][2])
    Ph = cmath.phase(Connectivity[0][2])

    # Sending end
    aux = abs(V_All[0])**2/abs(Connectivity[0][2])
    centreS = [aux * numpy.cos(Ph), aux * math.sin(Ph)]

    # Receiving end
    aux = -abs(V_All[1])**2/abs(Connectivity[0][2])
    centreR = [aux * numpy.cos(Ph), aux * math.sin(Ph)]

    return radius, centreR, centreS


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
        print('The network has %d branches and %d buses' %
              (Number_Branches, Number_Buses))
        print('______________________________')
        print('Branch | From - To | Impedance')
        print('------------------------------')
        for branch in range(Number_Branches):
            print('%5.0f  | %4.0f - %2.0f |' %
                  (branch+1, Connectivity[branch][0], Connectivity[branch][1]),
                  end=' ')
            print(Connectivity[branch][2])
        print('_______|___________|__________')

    # Build Ybus matrix
    Ybus = numpy.zeros((Number_Buses, Number_Buses), dtype=complex)
    for branch in range(Number_Branches):
        From = Connectivity[branch][0] - 1
        To = Connectivity[branch][1] - 1

        Y = 1/Connectivity[branch][2]
        B = complex(0, Connectivity[branch][3])

        if From >= 0 and To >= 0:
            Ybus[From][To] = -Y
            Ybus[To][From] = -Y

        if From >= 0:
            Ybus[From][From] += Y + B/2

        if To >= 0:
            Ybus[To][To] += Y + B/2

    if prnt:
        print('\nYbus = \n', Ybus)
    if flg:
        return Ybus


def PCR_01(PG, QG):

    global centreR, centreS, radius, Connectivity, Vs
    Load = [
        [2, complex(-PG, -QG)]
    ]
    Generator = [
        {'Bus': 1, 'V': Vr, '𝜃': 0}
    ]
    Axes = [0, 1, -0.3, 0.1]

    print('Adjust generation, especially Q1, to keep V1 at %.4f pu' % Vs)
    V_All, 𝜃_All, Threshold, Succes = bfs(Generator, Connectivity, Load)
    Results = get_Parameters(Connectivity, V_All, 𝜃_All, Succes)
    print('  V%d =  %7.4f ∠ %8.4f [pu][deg]' % (1, V_All[1],
                                                𝜃_All[0]*180/math.pi))
    print('  V%d =  %7.4f ∠ %8.4f [pu][deg]' % (2, V_All[0],
                                                -1*𝜃_All[1]*180/math.pi))

    y1 = -(radius**2 - (PG - centreS[0])**2)**0.5 + centreS[1]
    y2 = (radius**2 - (PG - centreS[0])**2)**0.5 + centreS[1]
    print('Consider Q1 = %.4f or Q1 = %.4f' % (y1, y2))
    P = -Results['Net_Power'][0].real/100
    Q = -Results['Net_Power'][0].imag/100
    plot_circles(centreR, centreS, radius, [P, Q], [PG, QG], Axes)


def PCR_02(P, Q):

    global centreR, centreS, radius, Connectivity, Generator, Vr
    Load = [
        [2, complex(P, Q)]
    ]
    Axes = [0, 1, -0.3, 0.1]
    print('Adjust the load, especially Q2, to keep V2 at %.4f pu' % Vr)

    V_All, 𝜃_All, Threshold, Succes = bfs(Generator, Connectivity, Load)
    Results = get_Parameters(Connectivity, V_All, 𝜃_All, Succes)
    for xb, V, 𝜃 in zip(range(len(V_All)), V_All, 𝜃_All):
        print('  V%d =  %7.4f ∠ %8.4f [pu][deg]' % (xb+1, V, 𝜃*180/math.pi))

    y1 = (radius**2 - (P - centreR[0])**2)**0.5 + centreR[1]
    y2 = -(radius**2 - (P - centreR[0])**2)**0.5 + centreR[1]
    print('Consider Q2 = %.4f or Q2 = %.4f' % (y1, y2))
    PG = Results['Net_Power'][0].real/100
    QG = Results['Net_Power'][0].imag/100

    plot_circles(centreR, centreS, radius, [P, Q], [PG, QG], Axes)


def Phasor_01(R, X):
    Connectivity = [
        [1, 2, complex(R, X), 0]
    ]
    Load = [
        [2, complex(0.1, 0.01)]
    ]
    Generator = [
        {'Bus': 1, 'V': 1, '𝜃': 0}
    ]
    V_All, 𝜃_All, Threshold, Succes = bfs(Generator, Connectivity, Load)
    if not Succes:
        print('The model failed to converge')
    Results = get_Parameters(Connectivity, V_All, 𝜃_All, Succes)
    print('  V%d =  %7.4f ∠ %8.4f [pu][deg]' % (1, V_All[0],
                                                𝜃_All[0]*180/math.pi))
    print('  V%d =  %7.4f ∠ %8.4f [pu][deg]' % (2, V_All[1],
                                                𝜃_All[1]*180/math.pi))
    print('  I  =  %7.4f ∠ %8.4f [pu][deg]' % (abs(Results['Current'][0]),
                                               cmath.phase(Results['Current']
                                                           [0])*180/math.pi))
    plot_phasor(Results, Connectivity)


def Phasor_Gen(t):
    B = 5
    # Y = complex(0, B)
    Ybus = [[-t**2*B, t*B], [t*B, -B]]
    Load = [
        [2, complex(0.5, 0.5)]
    ]
    Generator = [
        {'Bus': 1, 'V': .95, '𝜃': 0}
    ]

    P_Data, Q_Data = develop_PF_Equations(Load, Generator, Ybus, True, False)
    Bus_Data, Bus_Type = get_Bus_Type(Ybus, Load, Generator)
    V_All, 𝜃_All, Threshold, Succes = Newtons_Method(P_Data, Q_Data, Bus_Data,
                                                     Bus_Type, Generator, 0)
    print('Vs =  %7.4f ∠ %8.4f [pu][deg]' % (V_All[0], 𝜃_All[0]*180/math.pi))
    print('Vp =  %7.4f ∠ %8.4f [pu][deg]' % (V_All[1], 𝜃_All[1]*180/math.pi))


def plot_circles(centreR, centreS, radius, Point1=[None], Point2=[None],
                 Axes=[None]):
    '''Method to plot both powe circle diagrams'''
    circle1 = plt.Circle(centreS, radius, color='b', fill=False)
    circle2 = plt.Circle(centreR, radius, color='b', fill=False)
    fig, ax = plt.subplots()
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    plt.grid(linestyle='--')
    plt.xlabel('Real power [pu]')
    plt.ylabel('Reactive power [pu]')
    if Axes[0] is None:
        ax.set_xlim((min([centreS[0], centreR[0]])-radius,
                     max([centreS[0], centreR[0]])+radius))
        ax.set_ylim((min([centreS[1], centreR[1]])-radius,
                     max([centreS[1], centreR[1]])+radius))
    else:
        ax.set_xlim((Axes[0], Axes[1]))
        ax.set_ylim((Axes[2], Axes[3]))
    if Point1[0] is not None:
        plt.plot(Point1[0], Point1[1], marker='o', label='Load')
    if Point2[0] is not None:
        plt.plot(Point2[0], Point2[1], marker='o', label='Generation')
    plt.legend()
    plt.show()


def plot_phasor(Results, Connectivity):
    fig, ax = plt.subplots()
    Origin = [0, 0]

    mm = []
    m, Es = plot_vector(Origin, Results['Voltage'][0], ax, 'V1')
    mm.append(m)
    m, Er = plot_vector(Origin, Results['Voltage'][1], ax, 'V2')
    mm.append(m)
    m, _ = plot_vector(Origin, Results['Current'][0], ax, 'I')
    mm.append(m)
    VR = Results['Current'][0]*Connectivity[0][2].real
    m, OR = plot_vector(Er, VR, ax, 'IR')
    mm.append(m)
    VX = Results['Current'][0]*complex(0, Connectivity[0][2].imag)
    m, _ = plot_vector(OR, VX, ax, 'jIX')
    mm.append(m)
    lim = [1000, -1000]
    for m in mm:
        lim[0] = min(lim[0], m[0])
        lim[1] = max(lim[1], m[1])
    plt.grid()
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(lim[0], lim[1]+.001)
    plt.show()


def plot_phasor_Gen(Th):
    Ik = 0.4
    Ang = Th/180*math.pi
    X = complex(0, 0.5)

    aux = Ik/math.cos(Ang)
    I = complex(Ik, aux*math.sin(Ang))

    V = complex(1, 0)
    IX = -I*X
    E = V-IX

    fig, ax = plt.subplots()
    Origin = [0, 0]
    m, _ = plot_vector(Origin, V, ax, 'V')
    m, Er = plot_vector(Origin, E, ax, 'E')
    m, _ = plot_vector(Er, IX, ax, 'jIX')
    m, _ = plot_vector(Origin, I, ax, 'I')

    ax.set_xlim(-0.05, 1.07)
    ax.set_ylim(-0.1, 0.25)
    plt.grid()
    print('  V =  %7.4f ∠ %8.4f [pu][deg]' %
          (abs(V), cmath.phase(V)*180/math.pi))
    print('  E =  %7.4f ∠ %8.4f [pu][deg]' %
          (abs(E), cmath.phase(E)*180/math.pi))
    print('  I =  %7.4f ∠ %8.4f [pu][deg]' %
          (abs(I), cmath.phase(I)*180/math.pi))
    if Th == 0:
        print('Normal excitation')
    elif Th > 0:
        print('Under-excited')
    else:
        print('Overexcited')


def plot_vector(Ogn, Vec, ax=None, Nme=None, Coor=[0, 0]):
    '''Plot a vector'''

    V = [Vec.real, Vec.imag]

    plt.quiver(Ogn[0], Ogn[1], V[0], V[1], angles='xy', scale_units='xy',
               scale=1)

    if ax is not None:
        ax.annotate(Nme, xy=(Ogn[0]+V[0]/2+Coor[0], Ogn[1]+V[1]/2+Coor[1]),
                    fontsize=12)

    return [min([Ogn[1], Ogn[1]+V[1]]), max(Ogn[1], Ogn[1]+V[1])], \
        [Ogn[0]+V[0], Ogn[1]+V[1]]


def VC_01(P, Q, V):

    Connectivity = [
        [1, 2, complex(0, 0.1), 0]
    ]
    Load = [
        [2, complex(P, Q)]
    ]
    Generator = [
        {'Bus': 1, 'V': V, '𝜃': 0}
    ]
    V_All, 𝜃_All, Threshold, Succes = bfs(Generator, Connectivity, Load)
    for xb, V, 𝜃 in zip(range(len(V_All)), V_All, 𝜃_All):
        print('V%d =  %7.4f ∠ %8.4f [pu][deg]' % (xb+1, V, 𝜃*180/math.pi))

