"""
Author:       Eva Nieuwenhuis
University:   UvA
Student id':  13717405
Description:  Code with the model that simulates the dynamics in the multiple myeloma
              (MM) microenvironment with four cell types: drug-sensitive MM cells
              (MMd), resistant MM cells (MMr), osteoblasts (OBs) and osteoclasts
              (OCs). The model is a public goods game in the framework of evolutionary
              game theory with collective interactions and linear benefits. In this
              model there is looked at the fractions of the four cell types.
"""

# Import the needed libraries
import math
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import ternary
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from scipy.integrate import odeint
import csv
from scipy.optimize import minimize
from scipy.stats import spearmanr
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import pearsonr

"""
Example payoff matrix:
M = np.array([
       Goc Gob Gmmd Gmmr
    OC  [a,  b,  c,  d],
    OB  [e,  f,  g,  h],
    MMd [i,  j,  k,  l],
    MMr [m,  n,  o,  p]])
"""

def main():
    # Do doc tests
    import doctest
    doctest.testmod()

    # Make a figure showing the cell fraction dynamics by traditional therapy and
    # by adaptive therapy
    # list_t_steps_drug = [10, 10, 10]
    # Figure_conineous_MTD_vs_AT(12, list_t_steps_drug)
    #
    # # Make a 3D figure showthing the effect of different drug holiday and
    # # administration periods
    # Figure_3D_MM_frac_IH_add_and_holiday_()
    #
    # # Make a figure that shows the MM fraction for different bOC,MMd values
    # Figure_best_b_OC_MMd()

    # Make a figure that shows the MM fraction for different WMMd IH values
    Figure_best_WMMD_IH()
    #
    # # Make a 3D figure showing the effect of different WMMd and MMd GF IH strengths
    Figure_3D_MMd_IH_strength()

    # Make line plots showing different equilibriums when the MMd GF IH holiday and
    # administration durations changes
    list_t_steps_drug = [6, 8, 10]
    Figure_3_senarios_MMd_GF_IH(10, list_t_steps_drug)

    # Make line plots showing different equilibriums when the WMMd IH holiday and
    # administration durations changes
    list_t_steps_drug = [8, 10, 12]
    Figure_3_senarios_WMMd_IH(10, list_t_steps_drug)

    # Make line plots showing different equilibriums when the MMd GF IH and WMMd IH
    # holiday and administration durations changes
    list_t_steps_drug = [10, 12, 14]
    Figure_3_senarios_MMd_GF_WMMd_IH(8, list_t_steps_drug)

    # Make a figure that shows the cell fraction dynamics and fitness
    Figure_frac_fitness_dynamics()

    # Make tables showing the effect of chaning interaction matrix on the
    # eigenvalues H period, A period and MM fraction
    Dataframe_bOCMMd_eigenvalues()
    Dataframe_bMMdMMd_bMMrMMr_eigenvalues()



def fitness_WOC(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix):
    """
    Function that calculates the fitness of an osteoclast in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Number of individuals within the interaction range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.

    Returns:
    --------
    WOC: Float
        Fitness of an OC.

    Example:
    -----------
    >>> fitness_WOC(0.4, 0.2, 0.3, 0.1, 10, 0.3, 0.2, 0.3, 0.5, np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]]))
    0.10859999999999997
    """
    # Extract the needed matrix values
    a = matrix[0, 0]
    b = matrix[0, 1]
    c = matrix[0, 2]
    d = matrix[0, 3]

    # Calculate the fitness value
    WOC = (a*xOC*cOC + b*xOB*cOB + c*xMMd*cMMd + d* xMMr *cMMr)*(N - 1)/N - cOC
    return WOC

def fitness_WOB(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix):
    """
    Function that calculates the fitness of an osteoblast in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Number of individuals within the interaction range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.

    Returns:
    --------
    WOB: Float
        Fitness of an OB.

    Example:
    -----------
    >>> fitness_WOB(0.4, 0.2, 0.3, 0.1, 10, 0.3, 0.2, 0.3, 0.5, np.array([
    ...    [0.7, 1, 2.5, 2.1],
    ...    [1, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0, -0.2, 1.2]]))
    -0.020900000000000002
    """
    # Extract the necessary matrix values
    e = matrix[1, 0]
    f = matrix[1, 1]
    g = matrix[1, 2]
    h = matrix[1, 3]

    # Calculate the fitness value
    WOB = (e*xOC*cOC + f*xOB*cOB + g*xMMd*cMMd + h* xMMr*cMMr)*(N - 1)/N - cOB
    return WOB

def fitness_WMMd(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix,
                                                            WMMd_inhibitor = 0):
    """
    Function that calculates the fitness of a drug-senstive MM cell in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Number of individuals within the interaction range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    cMMr: Float
        Cost parameter MMr.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd.

    Returns:
    --------
    WMMd: Float
        Fitness of a MMd.

    Example:
    -----------
    >>> fitness_WMMd(0.4, 0.2, 0.3, 0.1, 10, 0.3, 0.2, 0.3, 0.5, np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]]), 0)
    0.05730000000000007
    """
    # Extract the necessary matrix values
    i = matrix[2, 0]
    j = matrix[2, 1]
    k = matrix[2, 2]
    l = matrix[2, 3]

    # Calculate the fitness value
    WMMd = (i*xOC*cOC + j*xOB*cOB + k*xMMd*cMMd + l* xMMr*cMMr - WMMd_inhibitor \
                                                        * cMMd)*(N - 1)/N - cMMd
    return WMMd

def fitness_WMMr(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix):
    """
    Function that calculates the fitness of a resistant MM cell in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMr: Float
        Fraction of the MMr.
    xMMd: Float
        Fraction of the MMd.
    N: Int
        Number of individuals within the interaction range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.

    Returns:
    --------
    WMMr: Float
        Fitness of a MMr.

    Example:
    -----------
    >>> fitness_WMMr(0.4, 0.2, 0.3, 0.1, 10, 0.3, 0.2, 0.3, 0.5, np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]]))
    -0.23539999999999994
    """
    # Extract the necessary matrix values
    m = matrix[3, 0]
    n = matrix[3, 1]
    o = matrix[3, 2]
    p = matrix[3, 3]

    # Calculate the fitness value
    WMMr = (m*xOC*cOC + n*xOB*cOB + o*xMMd*cMMd + p* xMMr*cMMr)*(N - 1)/N - cMMr
    return WMMr

def model_dynamics(y, t, N, cOC, cOB, cMMd, cMMr, matrix, WMMd_inhibitor = 0):
    """Function that determines the fracuenty dynamics in a population over time.

    Parameters:
    -----------
    y: List
        List with the values of xOC, xOB, xMMd and xMMr.
    t: Numpy.ndarray
        Array with all the time points.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd.

    Returns:
    --------
    [xOC_change, xOB_change, xMMd_change, xMMr_change]: List
        List containing the changes in fractions of OC, OB, MMd and MMr.

    Example:
    -----------
    >>> model_dynamics([0.4, 0.2, 0.3, 0.1], 1, 10, 0.3, 0.2, 0.3, 0.5, np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]]))
    [0.030275999999999983, -0.010762000000000006, 0.0073170000000000145, -0.026830999999999994]
    """
    xOC, xOB, xMMd, xMMr = y

    # Determine the fitness values
    WOC = fitness_WOC(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix)
    WOB = fitness_WOB(xOC, xOB, xMMd, xMMr,  N, cOC, cOB, cMMd, cMMr, matrix)
    WMMd = fitness_WMMd(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix,
                                                                WMMd_inhibitor)
    WMMr = fitness_WMMr(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix)

    # Determine the average fitness
    W_average = xOC * WOC + xOB * WOB + xMMd * WMMd + xMMr * WMMr

    # Determine the new fractions based on replicator dynamics
    xOC_change = xOC * (WOC - W_average)
    xOB_change = xOB * (WOB - W_average)
    xMMd_change = xMMd * (WMMd - W_average)
    xMMr_change = xMMr * (WMMr - W_average)

    # Make floats of the arrays
    xOC_change = float(xOC_change)
    xOB_change = float(xOB_change)
    xMMd_change = float(xMMd_change)
    xMMr_change = float(xMMr_change)

    return [xOC_change, xOB_change, xMMd_change, xMMr_change]


def frac_to_fitness_values(dataframe_fractions, N, cOC, cOB, cMMd, cMMr, matrix,
                                                            WMMd_inhibitor = 0):
    """Function that determines the fitness values of the OCs, OBs, MMd and MMr
    based on their fractions on every time point. It also calculates the average
    fitness.

    Parameters:
    -----------
    dataframe_fractions: Dataframe
        Dataframe with the fractions of the OBs, OCs MMd and MMr on every
        timepoint.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd

    Returns:
    --------
    dataframe_fitness: Dataframe
        A dataframe with the fitness values of the OBs, OCs, MMd and MMr and
        the average fitness on every time point.
    """
    # Make lists
    WOC_list = []
    WOB_list = []
    WMMd_list = []
    WMMr_list = []
    W_average_list = []
    generation_list = []

    # Iterate over each row
    for index, row in dataframe_fractions.iterrows():

        # Extract values of xOC, xOB, and xMM for the current row
        xOC = row['xOC']
        xOB = row['xOB']
        xMMd = row['xMMd']
        xMMr = row['xMMr']

        # Determine the fitness values
        WOC = fitness_WOC(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix)
        WOB = fitness_WOB(xOC, xOB, xMMd, xMMr,  N, cOC, cOB, cMMd, cMMr, matrix)
        WMMd = fitness_WMMd(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix,
                                                                WMMd_inhibitor)
        WMMr = fitness_WMMr(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix)

        # Determine the average fitness
        W_average = xOC * WOC + xOB * WOB + xMMd * WMMd + xMMr * WMMr

        # Add the calculated fitness values to the respective lists
        WOC_list.append(WOC)
        WOB_list.append(WOB)
        WMMd_list.append(WMMd)
        WMMr_list.append(WMMr)
        W_average_list.append(W_average)
        generation_list.append(index)

    # Create a datafrane with the calculated fitness values
    dataframe_fitness = pd.DataFrame({'Generation': generation_list,
                            'WOC': WOC_list, 'WOB': WOB_list, 'WMMd': WMMd_list,
                                'WMMr': WMMr_list, 'W_average': W_average_list})

    return(dataframe_fitness)

def save_dataframe(data_frame, file_name, folder_path):
    """ Function that saves a dataframe as csv file.

    Parameters:
    -----------
    data_frame: DataFrame
        The dataframe containing the collected data.
    file_name: String
        The name of the csv file.
    folder_path: String
        Path to the folder where the data will be saved.
    """
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    data_frame.to_csv(file_path, index=False)

def save_dictionary(dictionary, file_path):
    """ Function that saves a dictionary as csv file.

    Parameters:
    -----------
    dictionary: Dictionary
        The dictionary containing the collected data.
    file_path: String
        The name of the csv file and the path where the dictionary will be saved.
    """
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Create a header
        writer.writerow(['Key', 'Value'])

        # Loop over the rows
        for key, value in dictionary.items():
            writer.writerow([str(key), str(value)])

def save_Figure(Figure, file_name, folder_path):
    """Save the Figure to a specific folder.

    Parameters:
    -----------
    Figure: Matplotlib Figure
        Figure object that needs to be saved.
    file_name: String
        The name for the plot.
    folder_path: String:
        Path to the folder where the data will be saved.
    """
    os.makedirs(folder_path, exist_ok=True)
    Figure.savefig(os.path.join(folder_path, file_name))


def switch_dataframe(n_switches, t_steps_drug, t_steps_no_drug, xOC, xOB, xMMd, xMMr,
    N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor = 0):
    """ Function that makes a dataframe of the xOC, xOB, xMMd and xMMr values over
    time for a given time of drug holiday and administration periods.

    Parameters:
    -----------
    n_switches: Int
        The number of switches between giving drugs and not giving drugs.
    t_steps_drug: Int
        The number of generations drugs are administared.
    t_steps_no_drug: Int
        The number of generations drugs are not administared.
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMr: Float
        Fraction of the MMr.
    xMMd: Float
        Fraction of the MMd.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are administrated.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are administrated.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd.

    Returns:
    --------
    df_total_switch: Dataframe
        Dataframe with the xOC, xOB, xMMd and xMMr values over time.
    """
    # Set initial values
    x = 0
    time = 0
    df_total_switch = pd.DataFrame()
    t_steps = 15
    t = np.linspace(0, t_steps, t_steps*2)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_total_switch = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                    'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Increase the time
    time += t_steps

    # Perform a number of switches
    for i in range(n_switches):

        # If x = 0 make sure the MMd is inhibited
        if x == 0:

            # Determine the start fraction values
            xOC = df_total_switch['xOC'].iloc[-1]
            xOB = df_total_switch['xOB'].iloc[-1]
            xMMd = df_total_switch['xMMd'].iloc[-1]
            xMMr = df_total_switch['xMMr'].iloc[-1]

            # Payoff matrix
            matrix = matrix_GF_IH

            t = np.linspace(time, time + t_steps_drug, t_steps_drug)
            y0 = [xOC, xOB, xMMd, xMMr]
            parameters = (N, cOC, cOB, cMMd, cMMr, matrix, WMMd_inhibitor)

            # Determine the ODE solutions
            y = odeint(model_dynamics, y0, t, args=parameters)
            df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

            # Add dataframe tot total dataframe
            df_total_switch = pd.concat([df_total_switch, df])
            df_total_switch.reset_index(drop=True, inplace=True)

            # Change the x and time value
            x = 1
            time += t_steps_drug

        # If x = 1 make sure the MMd is not inhibited
        else:
            # Determine the start fraction values
            xOC = df_total_switch['xOC'].iloc[-1]
            xOB = df_total_switch['xOB'].iloc[-1]
            xMMd = df_total_switch['xMMd'].iloc[-1]
            xMMr = df_total_switch['xMMr'].iloc[-1]

            # Payoff matrix
            matrix = matrix_no_GF_IH

            t = np.linspace(time, time + t_steps_no_drug , t_steps_no_drug)
            y0 = [xOC, xOB, xMMd, xMMr]
            parameters = (N, cOC, cOB, cMMd, cMMr, matrix)

            # Determine the ODE solutions
            y = odeint(model_dynamics, y0, t, args=parameters)
            df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

            # Add dataframe tot total dataframe
            df_total_switch = pd.concat([df_total_switch, df])
            df_total_switch.reset_index(drop=True, inplace=True)

            # Change the x and time value
            x = 0
            time += t_steps_no_drug

    return df_total_switch

def pronto_switch_dataframe(n_switches, t_steps_drug, t_steps_no_drug, xOC, xOB,
                            xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH,
                            matrix_GF_IH, WMMd_inhibitor = 0):
    """ Function that makes a dataframe of the xOC, xOB, xMMd and xMMr values over
    time for a given time of drug holiday and administration periods. It starts
    immediately with switching.

    Parameters:
    -----------
    n_switches: Int
        The number of switches between giving drugs and not giving drugs.
    t_steps_drug: Int
        The number of generations drugs are administared.
    t_steps_no_drug: Int
        The number of generations drugs are not administared.
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMr: Float
        Fraction of the MMr.
    xMMd: Float
        Fraction of the MMd.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: float
        Cost parameter OBs.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are administrated.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are administrated.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd.

    Returns:
    --------
    df_total_switch: Dataframe
        Dataframe with the xOC, xOB, xMMd and xMMr values over time.
    """
    # Set initial values
    x = 0
    time = 0
    t = np.linspace(0, t_steps_no_drug, t_steps_no_drug*2)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_total_switch = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                    'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Increase the time
    time += t_steps_no_drug

    # Perform a number of switches
    for i in range(n_switches):

        # If x = 0 make sure the MMd is inhibited
        if x == 0:

            # Determine the start fraction values
            xOC = df_total_switch['xOC'].iloc[-1]
            xOB = df_total_switch['xOB'].iloc[-1]
            xMMd = df_total_switch['xMMd'].iloc[-1]
            xMMr = df_total_switch['xMMr'].iloc[-1]

            # Payoff matrix
            matrix = matrix_GF_IH

            t = np.linspace(time, time + t_steps_drug, t_steps_drug)
            y0 = [xOC, xOB, xMMd, xMMr]
            parameters = (N, cOC, cOB, cMMd, cMMr, matrix, WMMd_inhibitor)

            # Determine the ODE solutions
            y = odeint(model_dynamics, y0, t, args=parameters)
            df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

            # Add dataframe tot total dataframe
            df_total_switch = pd.concat([df_total_switch, df])
            df_total_switch.reset_index(drop=True, inplace=True)

            # Change the x and time value
            x = 1
            time += t_steps_drug

        # If x = 1 make sure the MMd is not inhibited
        else:
            # Determine the start fraction values
            xOC = df_total_switch['xOC'].iloc[-1]
            xOB = df_total_switch['xOB'].iloc[-1]
            xMMd = df_total_switch['xMMd'].iloc[-1]
            xMMr = df_total_switch['xMMr'].iloc[-1]

            # Payoff matrix
            matrix = matrix_no_GF_IH

            t = np.linspace(time, time + t_steps_no_drug , t_steps_no_drug)
            y0 = [xOC, xOB, xMMd, xMMr]
            parameters = (N, cOC, cOB, cMMd, cMMr, matrix)

            # Determine the ODE solutions
            y = odeint(model_dynamics, y0, t, args=parameters)
            df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

            # Add dataframe tot total dataframe
            df_total_switch = pd.concat([df_total_switch, df])
            df_total_switch.reset_index(drop=True, inplace=True)

            # Change the x and time value
            x = 0
            time += t_steps_no_drug

    return df_total_switch

def mimimal_tumour_frac_t_steps(t_steps_drug, t_steps_no_drug, xOC, xOB, xMMd, xMMr,
        N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor = 0):
    """ Function that makes a dataframe of the xOC, xOB, xMMd and xMMr values over
    time for a given time of a drug holiday.

    Parameters:
    -----------
    t_steps_drug: Int
        The number of generations drugs are administared.
    t_steps_no_drug: Int
        The number of generations drugs are not administared.
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMr: Float
        Fraction of the MMr.
    xMMd: Float
        Fraction of the MMd.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: float
        Cost parameter OBs.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are administrated.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are administrated.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd.

    Example:
    -----------
    average_MM_fractions: float
        The average total MM fraction in the last period.

    >>> matrix_no_GF_IH = np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]])
    >>> matrix_no_GF_IH = np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [0.8, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]])
    >>> mimimal_tumour_frac_t_steps(5, 5, 0.2, 0.3, 0.2, 0.3, 10, 0.3, 0.2,
    ...                               0.3, 0.5, matrix_no_GF_IH, matrix_no_GF_IH)
    -1.5588579521678917e-14
    """
    # Deteremine the number of switches
    time_step = (t_steps_drug + t_steps_no_drug) / 2
    n_switches = int((110 // time_step) -1)

    # Create a dataframe of the fractions
    df = switch_dataframe(n_switches, t_steps_drug, t_steps_no_drug, xOC, xOB,
                                 xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                                 matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor)

    # Determine the average MM fraction in the last period with and without drugs
    last_MM_fractions = df['total xMM'].tail(int(time_step *2))
    average_MM_fractions = last_MM_fractions.sum() / (int(time_step*2))

    return float(average_MM_fractions)


def mimimal_tumour_frac_b_OC_MMd(b_OC_MMd, xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
                                                    cMMr, matrix, t, b_OC_MMd_array):
    """Function that determines the fraction of the population being MM for a
    specific b_OC_MMd value.

    Parameters:
    -----------
    b_OC_MMd: Float
        Interaction value that gives the effect of the GFs of OCs on MMd.
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    t: Numpy.ndarray
        Array with all the time points.
    b_OC_MMd_array: Float
        If True b_OC_MMd is an array and if False b_OC_MMd is a float.

    Returns:
    --------
    last_MM_fraction: Float
        The total MM fraction.

    Example:
    -----------
    average_MM_fractions: float
        The average total MM fraction in the last period.

    >>> matrix = np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]])
    >>> mimimal_tumour_frac_b_OC_MMd(1, 0.2, 0.3, 0.2, 0.3, 10, 0.3, 0.2, 0.3, 0.5,
    ...                                      matrix, np.linspace(0, 10, 10), False)
    0.07254732036078437
    """
    # Change b_OC_MMd to a float if it is an array
    if b_OC_MMd_array == True:
        b_OC_MMd = b_OC_MMd[0]

    # Change the b_OC_MM value to the specified value
    matrix[2, 0]= b_OC_MMd

    # Set the initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the total MM fraction
    last_MM_fraction = df['total xMM'].iloc[-1]

    return float(last_MM_fraction)

def mimimal_tumour_frac_dev(WMMd_inhibitor, xOC, xOB, xMMd, xMMr, N, cOC, cOB,
                                    cMMd, cMMr, matrix, t, WMMd_inhibitor_array):
    """Function that determines the fraction of the population being MM for a
    specific wMMd drug inhibitor value.

    Parameters:
    -----------
    WMMd_inhibitor: Float
        Streght of the drugs that inhibits the cMMd.
    xOC: Float
        Fraction of OCs.
    xOB: Float
        Fraction of OBs.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Number of cells in the difussion range.
    cOC: Float
        Cost parameter OCs.
    cOB: Float
        Cost parameter OBs.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    t: Numpy.ndarray
        Array with all the time points.
    WMMd_inhibitor_array: Float
        If True WMMd_inhibitor is an array and if False WMMd_inhibitor is a float.

    Returns:
    --------
    last_MM_fraction: Float
        The total MM fraction.

    Example:
    -----------
    average_MM_fractions: float
        The average total MM fraction in the last period.

    >>> matrix = np.array([
    ...    [0.7, 1.0, 2.5, 2.1],
    ...    [1.0, 1.4, -0.3, 1.0],
    ...    [2.5, 0.2, 1.1, -0.2],
    ...    [2.1, 0.0, -0.2, 1.2]])
    >>> mimimal_tumour_frac_dev(1, 0.2, 0.3, 0.2, 0.3, 10, 0.3, 0.2, 0.3, 0.5,
    ...                                      matrix, np.linspace(0, 10, 10), False)
    0.038238963035331155
    """
    # Determine if WMMd_inhibitor is an array
    if WMMd_inhibitor_array == True:
        WMMd_inhibitor = WMMd_inhibitor[0]

    # Set initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the total MM fraction
    last_MM_fraction = df['total xMM'].iloc[-1]

    return float(last_MM_fraction)

""" Figure to determine best WMMD IH value """
def Figure_best_WMMD_IH():
    """ Function that shows the effect of different OB and OC cost values for
    different WMMd drug inhibitor values. It also determines the WMMd IH value
    causing the lowest total MM fraction."""

    # Set start values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.9
    cOC = 1.0
    xOC = 0.4
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.1

    # Payoff matrix
    matrix = np.array([
        [0.0, 1.6, 2.0, 1.8],
        [1.0, 0.0, -0.5, -0.5],
        [2.0, 0, 0.2, 0.0],
        [1.8, 0, -1.1, 0.2]])

    t = np.linspace(0, 100, 100)
    dev_start = 0.3

    # Perform the optimization
    result_high = minimize(mimimal_tumour_frac_dev, dev_start, args = (xOC, xOB,
                            xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix, t, True),
                                bounds=[(0, 0.8)], method='Nelder-Mead')

    # Retrieve the optimal value
    optimal_dev_high = result_high.x
    print("Optimal value for drug effect by high OB and OC cost values:",
        float(optimal_dev_high[0]), ', gives tumour fraction:', result_high.fun)

    # Make a dictionary
    dict_frac_tumour_high_c = {}

    # Loop over the different WMMd_inhibitor values
    for WMMd_inhibitor in range(3000):
        WMMd_inhibitor = WMMd_inhibitor/1000
        frac_tumour = mimimal_tumour_frac_dev(WMMd_inhibitor, xOC, xOB, xMMd, xMMr,
                                        N, cOC, cOB, cMMd, cMMr, matrix, t, False)
        dict_frac_tumour_high_c[WMMd_inhibitor] = frac_tumour

    # Save the data
    save_dictionary(dict_frac_tumour_high_c,
            r'..\data\data_own_model_fractions\dict_cell_frac_WMMd_IH_high_c.csv')

    # Make lists of the keys and the values
    keys_high_c = list(dict_frac_tumour_high_c.keys())
    values_high_c = list(dict_frac_tumour_high_c.values())

    # Set new cOC and cOB values and make a dictionary
    cOB = 0.8
    cOC = 0.9
    dict_frac_tumour_low_c = {}

    # Perform the optimization
    result_low = minimize(mimimal_tumour_frac_dev, dev_start, args = (xOC, xOB,
        xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix, t, True), bounds=[(0, 3)])

    # Retrieve the optimal value
    optimal_dev_low= result_low.x
    print("Optimal value for drug effect by low OB and OC cost value:",
            float(optimal_dev_low[0]),', gives tumour fraction:', result_low.fun)

    # Loop over the different WMMd_inhibitor values
    for WMMd_inhibitor in range(3000):
        WMMd_inhibitor = WMMd_inhibitor/1000
        frac_tumour = mimimal_tumour_frac_dev(WMMd_inhibitor, xOC, xOB, xMMd, xMMr,
                                        N, cOC, cOB, cMMd, cMMr, matrix, t, False)
        dict_frac_tumour_low_c[WMMd_inhibitor] = frac_tumour

    # Save the data
    save_dictionary(dict_frac_tumour_low_c,
            r'..\data\data_own_model_fractions\dict_cell_frac_WMMd_IH_low_c.csv')

    # Make lists of the keys and the values
    keys_low_c = list(dict_frac_tumour_low_c.keys())
    values_low_c = list(dict_frac_tumour_low_c.values())

    # Create a Figure
    plt.figure(figsize=(14, 8))

    # Subplot one
    plt.subplot(1, 2, 1)
    plt.plot(keys_high_c, values_high_c, color='purple')
    plt.title(r"""MM fraction for various $W_{MMd}$ IH strengths
     at cOB = 0.9 and cOC = 1.0""")
    plt.xlabel(r' $W_{MMd}$ strength')
    plt.ylabel('MM fraction')
    plt.grid(True)

    # Subplot two
    plt.subplot(1, 2, 2)
    plt.plot(keys_low_c, values_low_c, color='blue')
    plt.title(r"""MM fraction for various $W_{MMd}$ IH strengths
    at cOB = 0.8 and cOC = 0.9""")
    plt.xlabel(r' $W_{MMd}$ strength')
    plt.ylabel('MM fraction')

    plt.tight_layout()
    plt.grid(True)
    save_Figure(plt, 'line_plot_cell_frac_change_WMMd_IH_high_low_c',
                                 r'..\visualisation\results_own_model_fractions')
    plt.show()


""" Figure to determine best b_OC_MMd value """
def Figure_best_b_OC_MMd():
    """ Function that makes a Figure that shows the total MM fraction for different
    b_OC_MMd values. It also determines the b_OC_MMd value causing the lowest total
    MM fraction"""

    # Set start values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.4
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.1

    # Payoff matrix
    matrix = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.63, 0.2]])

    t = np.linspace(0, 100, 100)
    b_OC_MMd_start = 0.8

    # Perform the optimization
    result = minimize(mimimal_tumour_frac_b_OC_MMd, b_OC_MMd_start, args = (xOC,
        xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix, t, True), bounds=[(0, 3)])

    # Retrieve the optimal value
    optimal_b_OC_MMd= result.x
    print("Optimal value for b_OC_MMd:", float(optimal_b_OC_MMd[0]),
                                            'gives tumour fraction:', result.fun)

    # Make a dictionary
    dict_frac_tumour_GF = {}

    # Loop over all the b_OC_MMd values
    for b_OC_MMd in range(3000):
        b_OC_MMd = b_OC_MMd/1000

        # Determine the total MM fraction
        frac_tumour = mimimal_tumour_frac_b_OC_MMd(b_OC_MMd, xOC, xOB, xMMd, xMMr,
                                        N, cOC, cOB, cMMd, cMMr, matrix, t, False)
        dict_frac_tumour_GF[b_OC_MMd] = frac_tumour

    # Save the data
    save_dictionary(dict_frac_tumour_GF,
                 r'..\data\data_own_model_fractions\dict_cell_frac_b_OC_MMd.csv')

    # Make a list of the keys and one of the values
    b_OC_MMd_values = list(dict_frac_tumour_GF.keys())
    MM_fractions = list(dict_frac_tumour_GF.values())

    # Create the plot
    plt.plot(b_OC_MMd_values, MM_fractions, linestyle='-')
    plt.xlabel(r'$b_{OC, MMd}$ value ')
    plt.ylabel(r'Total MM fraction')
    plt.title(r'MM fraction for different $b_{OC, MMd}$ values')
    plt.grid(True)
    save_Figure(plt, 'line_plot_cell_frac_change_b_OC_MMd',
                                r'..\visualisation\results_own_model_fractions')
    plt.show()


""" Figure to determine the difference between traditional and adaptive therapy"""
def Figure_conineous_MTD_vs_AT(n_switches, t_steps_drug):
    """ Function that makes a figure with 6 subplots showing the cell type fraction
    dynamics by traditional therapy (continuous MTD) and adaptive therapy.

    Parameters:
    -----------
    n_switches: Int
        The number of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the number of time steps drugs are administared and the breaks
        are for the different Figures.
    """
    # Set initial parameter values
    N = 100
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.2
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.3

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [0.52, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_GF_IH_comb = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [1.23, 0, 0.2, 0.0],
        [1.9, 0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.5

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.14

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF = switch_dataframe(n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMD = switch_dataframe(n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb = switch_dataframe(n_switches, t_steps_drug[2],
                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_GF_IH_comb, WMMd_inhibitor_comb)

    t = np.linspace(0, 15, 15)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the current fractions
    xOC = df_1['xOC'].iloc[-1]
    xOB = df_1['xOB'].iloc[-1]
    xMMd = df_1['xMMd'].iloc[-1]
    xMMr = df_1['xMMr'].iloc[-1]

    t = np.linspace(15, 135, 120)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total_GF = pd.concat([df_1, df_2])

    # Set initial parameter values
    xOC = 0.2
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.3
    t = np.linspace(0, 15, 15)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the current fractions
    xOC = df_1['xOC'].iloc[-1]
    xOB = df_1['xOB'].iloc[-1]
    xMMd = df_1['xMMd'].iloc[-1]
    xMMr = df_1['xMMr'].iloc[-1]

    t = np.linspace(15, 135, 120)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total_wMMd = pd.concat([df_1, df_2])

    # Set initial parameter values
    xOC = 0.2
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.3
    t = np.linspace(0, 15, 15)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the current fractions
    xOC = df_1['xOC'].iloc[-1]
    xOB = df_1['xOB'].iloc[-1]
    xMMd = df_1['xMMd'].iloc[-1]
    xMMr = df_1['xMMr'].iloc[-1]

    t = np.linspace(15, 135, 120)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_GF_IH_comb, WMMd_inhibitor_comb)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total_comb = pd.concat([df_1, df_2])


    # Save the data
    save_dataframe(df_total_switch_GF, 'df_cell_frac_switch_GF_IH.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_WMMD, 'df_cell_frac_switch_WMMd_IH.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_comb, 'df_cell_frac_switch_comb_IH.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_total_GF, 'df_cell_frac_continuous_GF_IH.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_total_wMMd, 'df_cell_frac_continuous_WMMd_IH.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_total_comb, 'df_cell_frac_continuous_comb_IH.csv',
                                             r'..\data\data_own_model_fractions')

    # Create a Figure
    fig, axs = plt.subplots(2, 3, figsize=(20, 9))

    # Plot the data without drug holidays in the first plot
    df_total_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction', fontsize=11)
    axs[0, 0].set_title(f"Continuous MTD MMd GF IH ")
    axs[0, 0].grid(True)

    # Plot the data with drug holidays in the second plot
    df_total_wMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel(' ')
    axs[0, 1].set_title(r"Continuous MTD $W_{MMd}$ IH")
    axs[0, 1].grid(True)

    # Plot the data with drug holidays in the second plot
    df_total_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 2])
    axs[0, 2].set_xlabel(' ')
    axs[0, 2].set_ylabel(' ')
    axs[0, 2].set_title(r"Continuous MTD MMd GF IH and $W_{MMd}$ IH")
    axs[0, 2].grid(True)

    # Plot the data with drug holidays in the third plot
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations', fontsize=11)
    axs[1, 0].set_ylabel('Fraction', fontsize=11)
    axs[1, 0].set_title(f"Adaptive therapy MMd GF IH")
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_WMMD.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations', fontsize=11)
    axs[1, 1].set_ylabel(' ')
    axs[1, 1].set_title(r"Adaptive therapy $W_{MMd}$ IH")
    axs[1, 1].grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 2])
    axs[1, 2].set_xlabel('Generations', fontsize=11)
    axs[1, 2].set_ylabel(' ')
    axs[1, 2].set_title(r"Adaptive therapy MMd GF IH and $W_{MMd}$ IH")
    axs[1, 2].grid(True)
    save_Figure(plt, 'line_plot_cell_frac_AT_MTD',
                                 r'..\visualisation\results_own_model_fractions')

    # Create a single legend outside of all plots
    legend_labels = ['Fraction OC', 'Fraction OB', 'Fraction MMd', 'Fraction MMr']
    fig.legend(labels = legend_labels, loc='upper center', ncol=4, fontsize='large')

    plt.show()

""" 3D plot showing the best IH holiday and administration periods"""
def Figure_3D_MM_frac_IH_add_and_holiday_():
    """ Figure that makes three 3D plot that shows the average MM fraction for
    different holiday and administration periods of only MMd GF inhibitor, only
    WMMd inhibitor or both. It prints the IH administration periods and holidays
    that caused the lowest total MM fraction."""

    # Set initial parameter values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.2
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.3

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.77, 0.2]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [0.7, 0, 0.2, 0.0],
        [1.9, 0, -0.77, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_GF_IH_comb = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [1.4, 0, 0.2, 0.0],
        [1.9, 0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.7

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.0

    # Make a dataframe
    column_names = ['Generations no drug', 'Generations drug', 'MM fraction']
    df_holliday_GF_IH = pd.DataFrame(columns=column_names)

    # Loop over all the t_step values for drug administration and drug holidays
    for t_steps_no_drug in range(2, 22):

        for t_steps_drug in range(2, 22):
            frac_tumour = mimimal_tumour_frac_t_steps(t_steps_drug,
                            t_steps_no_drug, xOC, xOB, xMMd, xMMr, N, cOC,
                            cOB, cMMd, cMMr, matrix_no_GF_IH, matrix_GF_IH)

            # Add results to the dataframe
            new_row_df = pd.DataFrame([{'Generations no drug': int(t_steps_no_drug),
                                            'Generations drug': int(t_steps_drug),
                                             'MM fraction': float(frac_tumour)}])
            df_holliday_GF_IH = pd.concat([df_holliday_GF_IH, new_row_df],
                                                            ignore_index=True)

    # Save the data
    save_dataframe(df_holliday_GF_IH, 'df_cell_frac_best_MMd_GH_IH_holiday.csv',
                                             r'..\data\data_own_model_fractions')

    # Find the drug administration and holiday period causing the lowest MM fraction
    min_index_GF_IH = df_holliday_GF_IH['MM fraction'].idxmin()
    g_no_drug_min_GF_IH = df_holliday_GF_IH.loc[min_index_GF_IH,
                                                           'Generations no drug']
    g_drug_min_GF_IH = df_holliday_GF_IH.loc[min_index_GF_IH, 'Generations drug']
    frac_min_GF_IH = df_holliday_GF_IH.loc[min_index_GF_IH, 'MM fraction']

    print(f"""Lowest MM fraction: {frac_min_GF_IH}-> MMd GF IH holidays are
            {g_no_drug_min_GF_IH} generations and MMd GF IH administrations
            are {g_drug_min_GF_IH} generations""")

    # Avoid errors because of the wrong datatype
    df_holliday_GF_IH['Generations no drug'] = pd.to_numeric(df_holliday_GF_IH[\
                                        'Generations no drug'], errors='coerce')
    df_holliday_GF_IH['Generations drug'] = pd.to_numeric(df_holliday_GF_IH[\
                                        'Generations drug'],errors='coerce')
    df_holliday_GF_IH['MM fraction'] = pd.to_numeric(df_holliday_GF_IH[\
                                        'MM fraction'], errors='coerce')

    # Make a meshgrid for the plot
    X_GF_IH = df_holliday_GF_IH['Generations no drug'].unique()
    Y_GF_IH = df_holliday_GF_IH['Generations drug'].unique()
    X_GF_IH, Y_GF_IH = np.meshgrid(X_GF_IH, Y_GF_IH)
    Z_GF_IH = np.zeros((20, 20))

    # Fill the 2D array with the MM fraction values by looping over each row
    for index, row in df_holliday_GF_IH.iterrows():
        i = int(row.iloc[0]) - 2
        j = int(row.iloc[1]) - 2
        Z_GF_IH[j, i] = row.iloc[2]

    # Make a dataframe
    column_names = ['Generations no drug', 'Generations drug', 'MM fraction']
    df_holliday_W_IH = pd.DataFrame(columns=column_names)

    # Loop over al the t_step values for drug dministration and drug holidays
    for t_steps_no_drug in range(2, 22):

        for t_steps_drug in range(2, 22):
            frac_tumour = mimimal_tumour_frac_t_steps(t_steps_drug, t_steps_no_drug,
                                xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                                matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)

            # Add results to the dataframe
            new_row_df = pd.DataFrame([{'Generations no drug': int(t_steps_no_drug),
                                            'Generations drug': int(t_steps_drug),
                                             'MM fraction': float(frac_tumour)}])
            df_holliday_W_IH = pd.concat([df_holliday_W_IH, new_row_df],
                                                                ignore_index=True)

    # Save the data
    save_dataframe(df_holliday_W_IH, 'df_cell_frac_best_WMMd_IH_holiday.csv',
                                             r'..\data\data_own_model_fractions')

    # Find the drug administration and holiday period causing the lowest MM fraction
    min_index_W_IH = df_holliday_W_IH['MM fraction'].idxmin()
    g_no_drug_min_W_IH = df_holliday_W_IH.loc[min_index_W_IH,'Generations no drug']
    g_drug_min_W_IH = df_holliday_W_IH.loc[min_index_W_IH, 'Generations drug']
    frac_min_W_IH = df_holliday_W_IH.loc[min_index_W_IH, 'MM fraction']

    print(f"""Lowest MM fraction: {frac_min_W_IH} -> WMMd IH holidays are
                                    {g_no_drug_min_W_IH} generations and WMMd IH
                            administrations are {g_drug_min_W_IH} generations""")

    # Avoid errors because of the wrong datatype
    df_holliday_W_IH['Generations no drug'] = pd.to_numeric(df_holliday_W_IH[\
                                    'Generations no drug'], errors='coerce')
    df_holliday_W_IH['Generations drug'] = pd.to_numeric(df_holliday_W_IH[\
                                            'Generations drug'], errors='coerce')
    df_holliday_W_IH['MM fraction'] = pd.to_numeric(df_holliday_W_IH[\
                                                'MM fraction'], errors='coerce')

    # Make a meshgrid for the plot
    X_W_IH = df_holliday_W_IH['Generations no drug'].unique()
    Y_W_IH = df_holliday_W_IH['Generations drug'].unique()
    X_W_IH, Y_W_IH = np.meshgrid(X_W_IH, Y_W_IH)
    Z_W_IH = np.zeros((20, 20))

    # Fill the 2D array with the MM fraction values by looping over each row
    for index, row in df_holliday_W_IH.iterrows():
        i = int(row.iloc[0]) -2
        j = int(row.iloc[1]) -2
        Z_W_IH[j, i] = row.iloc[2]

    # Make a dataframe
    column_names = ['Generations no drug', 'Generations drug', 'MM fraction']
    df_holliday_comb = pd.DataFrame(columns=column_names)

    # Loop over al the t_step values for drug dministration and drug holidays
    for t_steps_no_drug in range(2, 22):

        for t_steps_drug in range(2, 22):
            frac_tumour = mimimal_tumour_frac_t_steps(t_steps_drug,
                t_steps_no_drug, xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_GF_IH_comb, WMMd_inhibitor_comb)

            # Add results to the dataframe
            new_row_df = pd.DataFrame([{'Generations no drug': int(t_steps_no_drug),
                                            'Generations drug': int(t_steps_drug),
                                            'MM fraction': float(frac_tumour)}])
            df_holliday_comb = pd.concat([df_holliday_comb, new_row_df],
                                                                ignore_index=True)

    # Save the data
    save_dataframe(df_holliday_comb, 'df_cell_frac_best_MMd_IH_holiday.csv',
                                             r'..\data\data_own_model_fractions')

    # Find the drug administration and holiday period causing the lowest MM fraction
    min_index_comb = df_holliday_comb['MM fraction'].idxmin()
    g_no_drug_min_comb = df_holliday_comb.loc[min_index_comb, 'Generations no drug']
    g_drug_min_comb = df_holliday_comb.loc[min_index_comb, 'Generations drug']
    frac_min_comb = df_holliday_comb.loc[min_index_comb, 'MM fraction']

    print(f"""Lowest MM fraction: {frac_min_comb}-> MMd IH holidays are
                    {g_no_drug_min_comb} generations and MMd IH administrations
                    are {g_drug_min_comb} generations""")

    # Avoid errors because of the wrong datatype
    df_holliday_comb['Generations no drug'] = pd.to_numeric(df_holliday_comb[\
                                        'Generations no drug'], errors='coerce')
    df_holliday_comb['Generations drug'] = pd.to_numeric(df_holliday_comb[\
                                            'Generations drug'], errors='coerce')
    df_holliday_comb['MM fraction'] = pd.to_numeric(df_holliday_comb[\
                                            'MM fraction'], errors='coerce')

    # Make a meshgrid for the plot
    X_comb = df_holliday_comb['Generations no drug'].unique()
    Y_comb = df_holliday_comb['Generations drug'].unique()
    X_comb, Y_comb = np.meshgrid(X_comb, Y_comb)
    Z_comb = np.zeros((20, 20))

    # Fill the 2D array with the MM fraction values by looping over each row
    for index, row in df_holliday_comb.iterrows():
        i = int(row.iloc[0]) - 2
        j = int(row.iloc[1]) - 2
        Z_comb[j, i] = row.iloc[2]

    # Create a figure and a grid of subplots
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), subplot_kw={'projection': '3d'},
                                    gridspec_kw={'hspace': 0.25, 'wspace': 0.25})

    # Plot each subplot
    for i, ax in enumerate(axes.flat, start=1):
        if i == 1:
            surf = ax.plot_surface(X_W_IH, Y_W_IH, Z_W_IH, cmap='coolwarm')

            # Add labels
            ax.set_xlabel('Generations no IH')
            ax.set_ylabel('Generations IH')
            ax.set_zlabel('MM fraction')
            ax.set_title(r'A) $W_{MMd}$ inhibitor', pad=10)

            # Turn to the right angle
            ax.view_init(elev = 28, azim = -127)

            # Add a color bar
            color_bar = fig.colorbar(surf, ax=ax, shrink=0.4, location= 'right')
            color_bar.set_label('MM fraction')

        elif i == 2:
            surf = ax.plot_surface(X_GF_IH, Y_GF_IH, Z_GF_IH, cmap = 'coolwarm')

            # Add labels
            ax.set_xlabel('Generations no IH')
            ax.set_ylabel('Generations IH')
            ax.set_zlabel('MM fraction')
            ax.set_title('B)  MMd GF inhibitor', pad=10)

            # Turn to the right angle
            ax.view_init(elev = 32, azim = -128)

            # Add a color bar
            color_bar = fig.colorbar(surf, ax=ax, shrink=0.4, location= 'right')

            color_bar.set_label('MM fraction')

        elif i == 3:
            surf = ax.plot_surface(X_comb, Y_comb, Z_comb, cmap = 'coolwarm')

            # Add labels
            ax.set_xlabel('Generations no IHs')
            ax.set_ylabel('Generations IHs')
            ax.set_zlabel('MM fraction')
            ax.set_title('C)  $W_{MMd}$ inhibitor and MMd GF inhibitor', pad=10)

            # Turn to the right angle
            ax.view_init(elev = 40, azim = -142)

            # Add a color bar
            color_bar = fig.colorbar(surf, ax=ax, shrink=0.4, location= 'right')
            color_bar.set_label('MM fraction')

        else:
            # Hide the emply subplot
            ax.axis('off')

    # Add a color bar
    save_Figure(fig, '3d_plot_MM_frac_best_IH_h_a_periods',
                                r'..\visualisation\results_own_model_fractions')
    plt.show()

""" 3D plot showing the best IH strengths """
def Figure_3D_MMd_IH_strength():
    """ 3D plot that shows the average MM fraction for different MMd GF inhibitor
    and WMMd inhibitor strengths.It prints the IH streghts that caused the lowest
    total MM fraction."""

    # Set initial parameter values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.2
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.3

    # Payoff matrix when no drugs are pressent
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.77, 0.2]])

    # Payoff matrix when GF inhibitor drugs are pressent
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [1.5, 0, 0.2, 0.0],
        [1.9, 0, -0.77, 0.2]])

    # Administration and holiday periods
    t_steps_drug = 8
    t_steps_no_drug = 8

    # Make a dataframe
    column_names = ['Strength WMMd IH', 'Strength MMd GF IH', 'MM fraction']
    df_holliday = pd.DataFrame(columns=column_names)

    # Loop over al the t_step values for drug dministration and drug holidays
    for strength_WMMd_IH in range(0, 21):

        # Drug inhibitor effect
        WMMd_inhibitor = strength_WMMd_IH / 10
        for strength_MMd_GF_IH in range(0, 21):

            # Change effect of GF of OC on MMd
            matrix_GF_IH[2, 0] = 2.2 - round((strength_MMd_GF_IH / 10), 1)

            # Change how fast the MMr will be stronger than the MMd
            matrix_GF_IH[3, 2] = -0.77 - round((WMMd_inhibitor + \
                                    round((strength_MMd_GF_IH / 10), 1))/ 20, 3)

            frac_tumour = mimimal_tumour_frac_t_steps(t_steps_drug, t_steps_no_drug,
                                    xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                                    matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor)

            # Add results to the dataframe
            new_row_df = pd.DataFrame([{'Strength WMMd IH':\
                        round(strength_WMMd_IH/ 10, 1), 'Strength MMd GF IH': \
                round(strength_MMd_GF_IH/ 10, 1), 'MM fraction': frac_tumour}])

            df_holliday = pd.concat([df_holliday, new_row_df], ignore_index=True)

    # Save the data
    save_dataframe(df_holliday, 'df_cell_frac_best_MMd_IH_strength.csv',
                                             r'..\data\data_own_model_fractions')


    # Find the drug administration and holiday period causing the lowest MM fraction
    min_index = df_holliday['MM fraction'].idxmin()
    strength_WMMd_min = df_holliday.loc[min_index, 'Strength WMMd IH']
    strength_MMd_GF_min = df_holliday.loc[min_index, 'Strength MMd GF IH']
    frac_min = df_holliday.loc[min_index, 'MM fraction']

    print(f"""Lowest MM fraction: {frac_min}-> MMd GF IH strength is
        {strength_MMd_GF_min} and WMMd IH strength is {strength_WMMd_min}""")

    # Avoid errors because of the wrong datatype
    df_holliday['Strength WMMd IH'] = pd.to_numeric(df_holliday[\
                                        'Strength WMMd IH'], errors='coerce')
    df_holliday['Strength MMd GF IH'] = pd.to_numeric(df_holliday[\
                                        'Strength MMd GF IH'], errors='coerce')
    df_holliday['MM fraction'] = pd.to_numeric(df_holliday['MM fraction'],
                                                                errors='coerce')

    # Make a meshgrid for the plot
    X = df_holliday['Strength WMMd IH'].unique()
    Y = df_holliday['Strength MMd GF IH'].unique()
    X, Y = np.meshgrid(X, Y)
    Z = np.zeros((21, 21))

    # Fill the 2D array with the MM fraction values by looping over each row
    for index, row in df_holliday.iterrows():
        i = int(row.iloc[0]*10)
        j = int(row.iloc[1]*10)
        Z[j, i] = row.iloc[2]

    # Make a 3D Figure
    fig = plt.figure(figsize = (8, 6))
    ax = fig.add_subplot(111, projection = '3d')
    surf = ax.plot_surface(X, Y, Z, cmap = 'coolwarm')

    # Add labels
    ax.set_xlabel('Strength WMMd IH')
    ax.set_ylabel('Strength MMd GF IH')
    ax.set_zlabel('MM fraction')
    ax.set_title("""Average MM fraction with varing WMMd inhibitor and MMd
    GF inhibitor strengths""")

    # Turn to the right angle
    ax.view_init(elev = 40, azim = -70)

    # Add a color bar
    color_bar = fig.colorbar(surf, shrink = 0.6, location= 'left')
    color_bar.set_label('MM fraction')

    save_Figure(fig, '3d_plot_MM_frac_best_IH_strength',
                                r'..\visualisation\results_own_model_fractions')
    plt.show()

""" Figure with different GF IH administration and holliday periods"""
def Figure_3_senarios_MMd_GF_IH(n_switches, t_steps_drug):
    """ Function that makes a Figure that shows the effect of drug holidays.

    Parameters:
    -----------
    n_switches: Int
        The number of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the number of time steps drugs are administared and the breaks
        are for the different Figures.
    """
    # Set start parameter values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.3
    xOB = 0.2
    xMMd = 0.2
    xMMr = 0.3

    # Payoff matrices
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.7605, 0.2]])

    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [0.7, 0, 0.2, 0.0],
        [1.9, 0, -0.7605, 0.2]])

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_1 = pronto_switch_dataframe(n_switches, t_steps_drug[0],
                        t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
                        cMMr, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_2 = pronto_switch_dataframe(n_switches, t_steps_drug[1],
                        t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
                        cMMr, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_3 = pronto_switch_dataframe(n_switches, t_steps_drug[2],
                        t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
                         cMMr, matrix_no_GF_IH, matrix_GF_IH)

    t = np.linspace(0, 20, 20)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the current fractions
    xOC = df_1['xOC'].iloc[-1]
    xOB = df_1['xOB'].iloc[-1]
    xMMd = df_1['xMMd'].iloc[-1]
    xMMr = df_1['xMMr'].iloc[-1]

    t = np.linspace(20, 100, 80)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total = pd.concat([df_1, df_2])

    # Save the data
    save_dataframe(df_total_switch_1, 'df_cell_frac_G6_MMd_GF_inhibit.csv',
                                         r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_2, 'df_cell_frac_G8_MMd_GF_inhibit.csv',
                                         r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_3, 'df_cell_frac_G12_MMd_GF_inhibit.csv',
                                         r'..\data\data_own_model_fractions')
    save_dataframe(df_total, 'df_cell_frac_MMd_GF_inhibit_continuously.csv',
                                         r'..\data\data_own_model_fractions')

    # Create a Figure
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    g = 'generations'
    t = t_steps_drug

    # Plot the data without drug holidays in the first plot
    df_total.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[ \
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('MM fraction')
    axs[0, 0].set_title(f'Dynamics when MMd GF inhibitors are administered continuously')
    axs[0, 0].legend(loc = 'upper right')
    axs[0, 0].grid(True)

    # Plot the data with drug holidays in the second plot
    df_total_switch_1.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel('MM fraction')
    axs[0, 1].set_title(f'Dynamics when MMd GF inhibitors are administered every {t[0]} {g}')
    axs[0, 1].legend(loc = 'upper right')
    axs[0, 1].grid(True)

    # Plot the data with drug holidays in the third plot
    df_total_switch_2.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations')
    axs[1, 0].set_ylabel('MM fraction')
    axs[1, 0].set_title(f'Dynamics when MMd GF inhibitors are administered every {t[1]} {g}')
    axs[1, 0].legend(loc = 'upper right')
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_3.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations')
    axs[1, 1].set_ylabel('MM fraction')
    axs[1, 1].set_title(f'Dynamics when MMd GF inhibitors are administered every {t[2]} {g}')
    axs[1, 1].legend(loc = 'upper right')
    axs[1, 1].grid(True)
    save_Figure(plt, 'line_plot_cell_frac_MMd_GF_inhibit',
                                 r'..\visualisation\results_own_model_fractions')
    plt.show()

""" Figure with different WMMd IH administration and holliday periods"""
def Figure_3_senarios_WMMd_IH(n_switches, t_steps_drug):
    """ Function that makes a Figure that shows the effect of the time of a
    drug holiday and administration period.

    Parameters:
    -----------
    n_switches: Int
        The number of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the number of time steps drugs are administared and the breaks
        are for the different Figures.
    """
    # Set start parameter values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.3
    xOB = 0.2
    xMMd = 0.2
    xMMr = 0.3

    # Payoff matrix
    matrix = np.array([
        [0.0, 1.6, 2.2, 1.8],
        [1.0, 0.0, -0.5, -0.5],
        [2.4, 0, 0.2, 0.0],
        [1.8, 0, -0.754, 0.2]])

    WMMd_inhibitor = 1.33

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_1 = pronto_switch_dataframe(n_switches, t_steps_drug[0],
                            t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB,
                            cMMd, cMMr, matrix, matrix, WMMd_inhibitor)
    df_total_switch_2 = pronto_switch_dataframe(n_switches, t_steps_drug[1],
                            t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB,
                            cMMd, cMMr, matrix, matrix, WMMd_inhibitor)
    df_total_switch_3 = pronto_switch_dataframe(n_switches, t_steps_drug[2],
                            t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB,
                            cMMd, cMMr, matrix, matrix, WMMd_inhibitor)

    t = np.linspace(0, 20, 20)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the current fractions
    xOC = df_1['xOC'].iloc[-1]
    xOB = df_1['xOB'].iloc[-1]
    xMMd = df_1['xMMd'].iloc[-1]
    xMMr = df_1['xMMr'].iloc[-1]

    t = np.linspace(20, 100, 80)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total = pd.concat([df_1, df_2])

    # Save the data
    save_dataframe(df_total_switch_1, 'df_cell_frac_G8_WMMd_inhibit.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_2, 'df_cell_frac_G10_WMMd_inhibit.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_3, 'df_cell_frac_G12_WMMd_inhibit.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_total, 'df_cell_frac_WMMd_inhibit_continuously.csv',
                                             r'..\data\data_own_model_fractions')

    # Create a Figure
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    g = 'generations'
    t = t_steps_drug

    # Plot the data without drug holidays in the first plot
    df_total.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[ \
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('MM fraction')
    axs[0, 0].set_title(f'Dynamics when drugs are administered continuously')
    axs[0, 0].legend(loc = 'upper right')
    axs[0, 0].grid(True)

    # Plot the data with drug holidays in the second plot
    df_total_switch_1.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel('MM fraction')
    axs[0, 1].set_title(f'Dynamics when WMMd inhibitors are administered every {t[0]} {g}')
    axs[0, 1].legend(loc = 'upper right')
    axs[0, 1].grid(True)

    # Plot the data with drug holidays in the third plot
    df_total_switch_2.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations')
    axs[1, 0].set_ylabel('MM fraction')
    axs[1, 0].set_title(f'Dynamics when WMMd inhibitors are administered every {t[1]} {g}')
    axs[1, 0].legend(loc = 'upper right')
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_3.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations')
    axs[1, 1].set_ylabel('MM fraction')
    axs[1, 1].set_title(f'Dynamics when WMMd inhibitors are administered every {t[2]} {g}')
    axs[1, 1].legend(loc = 'upper right')
    axs[1, 1].grid(True)
    save_Figure(plt, 'line_plot_cell_frac_WMMd_inhibit',
                                 r'..\visualisation\results_own_model_fractions')
    plt.show()

""" Figure with different IH administration and holliday periods"""
def Figure_3_senarios_MMd_GF_WMMd_IH(n_switches, t_steps_drug):
    """ Function that makes a Figure that shows the effect of drug holidays.

    Parameters:
    -----------
    n_switches: Int
        The number of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the number of time steps drugs are administared and the breaks
        are for the different Figures.
    """
    # Set start parameter values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.3
    xOB = 0.2
    xMMd = 0.2
    xMMr = 0.3

    # Payoff matrices
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    matrix_GF_IH_half = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [1.4, 0, 0.2, 0.0],
        [1.9, 0, -1.0, 0.2]])

    WMMd_inhibitor_half = 0.514

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_1 = pronto_switch_dataframe(n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_GF_IH_half, WMMd_inhibitor_half)
    df_total_switch_2 = pronto_switch_dataframe(n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_GF_IH_half, WMMd_inhibitor_half)
    df_total_switch_3 = pronto_switch_dataframe(n_switches, t_steps_drug[2],
                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                matrix_no_GF_IH, matrix_GF_IH_half, WMMd_inhibitor_half)

    t = np.linspace(0, 20, 20)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Determine the current fractions
    xOC = df_1['xOC'].iloc[-1]
    xOB = df_1['xOB'].iloc[-1]
    xMMd = df_1['xMMd'].iloc[-1]
    xMMr = df_1['xMMr'].iloc[-1]

    t = np.linspace(20, 100, 80)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_GF_IH_half, WMMd_inhibitor_half)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total = pd.concat([df_1, df_2])

    # Save the data
    save_dataframe(df_total_switch_1, 'df_cell_frac_G10_MMd_GF_WMMd_inhibit.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_2, 'df_cell_frac_G12_MMd_GF_WMMd_inhibit.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_total_switch_3, 'df_cell_frac_G14_MMd_GF_WMMd_inhibit.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_total, 'df_cell_frac_MMd_GF_WMMd_inhibit_continuously.csv',
                                             r'..\data\data_own_model_fractions')

    # Create a Figure
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))

    # Plot the data without drug holidays in the first plot
    df_total.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[ \
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('MM fraction')
    axs[0, 0].set_title(f"""Dynamics when MMd GF and WMMd inhibitors
    are administered continuously""")
    axs[0, 0].legend(loc = 'upper right')
    axs[0, 0].set_xticklabels([])
    axs[0, 0].grid(True)

    # Plot the data with drug holidays in the second plot
    df_total_switch_1.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel('MM fraction')
    axs[0, 1].set_title(f"""Dynamics when MMd GF and WMMd inhibitors are
    administered every {t_steps_drug[0]} generations""")
    axs[0, 1].legend(loc = 'upper right')
    axs[0, 1].set_xticklabels([])
    axs[0, 1].grid(True)

    # Plot the data with drug holidays in the third plot
    df_total_switch_2.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations')
    axs[1, 0].set_ylabel('MM fraction')
    axs[1, 0].set_title(f"""Dynamics when MMd GF and WMMd inhibitors are
    administered every {t_steps_drug[0]} generations""")
    axs[1, 0].legend(loc = 'upper right')
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_3.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'], label=[\
    'fraction OC', 'fraction OB', 'fraction MMd','fraction MMr'], ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations')
    axs[1, 1].set_ylabel('MM fraction')
    axs[1, 1].set_title(f"""Dynamics when MMd GF and WMMd inhibitors are
    administered every {t_steps_drug[0]} generations""")
    axs[1, 1].legend(loc = 'upper right')
    axs[1, 1].grid(True)
    save_Figure(plt, 'line_plot_cell_frac_MMd_GF_WMMd_inhibit',
                                r'..\visualisation\results_own_model_fractions')
    plt.show()

""" Figure showing the fraction and fitness dynamics"""
def Figure_frac_fitness_dynamics():
    """Function that makes Figure of the OC, OB, MMd and MMr fraction and fitness
     values over the time"""

    # Set start values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1
    xOC = 0.15
    xOB = 0.4
    xMMd = 0.25
    xMMr = 0.2

    # Payoff matrix
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.9, 0.0, -0.5, -0.5],
        [2.2, 0.0, 0.2, 0.0],
        [1.9, 0.0, -0.77, 0.2]])

    t = np.linspace(0, 25, 25)

    # Initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1_MMd_GF_inhibition = pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Determine the current fractions
    xOC = df_1_MMd_GF_inhibition['xOC'].iloc[-1]
    xOB = df_1_MMd_GF_inhibition['xOB'].iloc[-1]
    xMMd = df_1_MMd_GF_inhibition['xMMd'].iloc[-1]
    xMMr = df_1_MMd_GF_inhibition['xMMr'].iloc[-1]

    # Payoff matrix
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [1.0, 0.0, -0.5, -0.5],
        [0.6, 0, 0.2, 0],
        [2.1, 0, -0.77, 0.2]])

    # Initial conditions
    t = np.linspace(25, 100, 75)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2_MMd_GF_inhibition = pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Combine the dataframes
    df_MMd_GF_inhibition = pd.concat([df_1_MMd_GF_inhibition,
                                                        df_2_MMd_GF_inhibition])

    # Set new start parameter values
    xOC = 0.15
    xOB = 0.4
    xMMd = 0.25
    xMMr = 0.2
    t = np.linspace(0, 25, 25)

    # Initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1_WMMd_inhibition = pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Determine the current fractions
    xOC = df_1_WMMd_inhibition['xOC'].iloc[-1]
    xOB = df_1_WMMd_inhibition['xOB'].iloc[-1]
    xMMd = df_1_WMMd_inhibition['xMMd'].iloc[-1]
    xMMr = df_1_WMMd_inhibition['xMMr'].iloc[-1]

    # Initial conditions
    t = np.linspace(25, 100, 75)
    WMMd_inhibitor =  1.4
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2_WMMd_inhibition = pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Combine the dataframes
    df_WMMd_inhibition = pd.concat([df_1_WMMd_inhibition, df_2_WMMd_inhibition])

    # Make dataframes for the fitness values
    df_fitness_WMMd_inhibition_1 = frac_to_fitness_values(df_1_WMMd_inhibition, N,
                                          cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)
    df_fitness_WMMd_inhibition_2 = frac_to_fitness_values(df_2_WMMd_inhibition, N,
                         cOC, cOB, cMMd, cMMr, matrix_no_GF_IH, WMMd_inhibitor)
    df_fitness_WMMd_inhibition = pd.concat([df_fitness_WMMd_inhibition_1,
                                df_fitness_WMMd_inhibition_2], ignore_index=True)

    df_fitness_MMd_GF_inhibition_1 = frac_to_fitness_values(df_1_MMd_GF_inhibition,
                                       N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)
    df_fitness_MMd_GF_inhibition_2 = frac_to_fitness_values(df_2_MMd_GF_inhibition,
                                          N, cOC, cOB, cMMd, cMMr, matrix_GF_IH)
    df_fitness_MMd_GF_inhibition = pd.concat([df_fitness_MMd_GF_inhibition_1,
                              df_fitness_MMd_GF_inhibition_2], ignore_index=True)

    # Save the data
    save_dataframe(df_WMMd_inhibition, 'df_cell_frac_cWMMd_inhibit.csv',
                                            r'..\data\data_own_model_fractions')
    save_dataframe(df_MMd_GF_inhibition, 'df_cell_frac_MMd_GF_inhibit.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_fitness_WMMd_inhibition, 'df_fitness_WMMd_inhibit.csv',
                                             r'..\data\data_own_model_fractions')
    save_dataframe(df_fitness_MMd_GF_inhibition, 'df_fitness_MMd_GF_inhibit.csv',
                                            r'..\data\data_own_model_fractions')

    # Create a Figure
    fig, axs = plt.subplots(2, 2, figsize=(16, 8))

    # Plot first subplot
    df_WMMd_inhibition.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                        label=['fraction OC', 'fraction OB', 'fraction MMd',
                                 'fraction MMr'], ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction')
    axs[0, 0].set_title(r'Fraction dynamics when a $W_{MMd}$ inhibitor is administerd')
    axs[0, 0].legend(loc = 'upper right')
    axs[0, 0].grid(True)

    # Plot the second subplot
    df_fitness_WMMd_inhibition.plot(y=['WOC', 'WOB', 'WMMd', 'WMMr', 'W_average'],
                                label = ['Fitness OC', 'Fitness OB', 'Fitness MMd',
                                  'Fitness MMr', 'Average fitness'],  ax=axs[1, 0])
    axs[1, 0].set_title(r'Fitness dynamics when a $W_{MMd}$ inhibitor is administerd')
    axs[1, 0].set_xlabel('Generations')
    axs[1, 0].set_ylabel('Fitness')
    axs[1, 0].legend(['Fitness OC', 'Fitness OB', 'Fitness MMd', 'Fitness MMr',
                                                        'Average fitness'])
    axs[1, 0].legend(loc = 'upper right')
    axs[1, 0].grid(True)

    # Plot the third subplot
    df_MMd_GF_inhibition.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                        label=['fraction OC', 'fraction OB', 'fraction MMd',
                                                'fraction MMr'], ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel('Fraction')
    axs[0, 1].set_title('Fraction dynamics when a MMd GF inhibitor is administerd')
    axs[0, 1].legend(loc = 'upper right')
    axs[0, 1].grid(True)

    # Plot the fourth subplot
    df_fitness_MMd_GF_inhibition.plot(y=['WOC', 'WOB', 'WMMd', 'WMMr', 'W_average'],
                              label = ['Fitness OC', 'Fitness OB', 'Fitness MMd',
                                 'Fitness MMr', 'Average fitness'],  ax=axs[1, 1])
    axs[1, 1].set_title('Fitness dynamics when a MMd GF inhibitor is administerd')
    axs[1, 1].set_xlabel('Generations')
    axs[1, 1].set_ylabel('Fitness')
    axs[1, 1].legend(loc = 'upper right')
    axs[1, 1].grid(True)
    plt.tight_layout()
    save_Figure(plt, 'line_plot_cell_frac_fitness_drugs',
                                r'..\visualisation\results_own_model_fractions')
    plt.show()


"""Tables showing the effect of chaning interaction matrix on the eigenvalues H
period, A period and MM fraction"""

def Dataframe_bOCMMd_eigenvalues():
    """ Function that makes a table of the eigenvalues of the interaction matrix,
    MM fraction and the best holiday (H) and administration (A) period for
    different bOC,MMd values."""

    # Make a dataframe
    column_names = ['bOC,MMd', 'Eigenvalue 1', 'Eigenvalue 2', 'Eigenvalue 3',
                        'Eigenvalue 4', 'period H', 'period A', 'MM fraction']
    df_eigenvalues = pd.DataFrame(columns=column_names)
    df_eigenvalues_float = pd.DataFrame(columns=column_names)

    for i in range(7):
        # Set initial parameter values
        N = 50
        cMMr = 1.3
        cMMd = 1.2
        cOB = 0.8
        cOC = 1
        xOC = 0.2
        xOB = 0.3
        xMMd = 0.2
        xMMr = 0.3

        # Payoff matrix when no drugs are present
        matrix_no_drugs = np.array([
            [0.0, 1.6, 2.2, 1.9],
            [1.0, 0.0, -0.5, -0.5],
            [2.2, 0.0, 0.2, 0.0],
            [1.9, 0.0, -0.8, 0.2]])

        # Payoff matrix when only GF inhibitor drugs are present
        matrix_drugs = np.array([
            [0.0, 1.6, 2.2, 1.9],
            [1.0, 0.0, -0.5, -0.5],
            [0.7,  0, 0.2, 0],
            [1.9, 0, -0.8, 0.2]])

        # Change the interaction value
        matrix_drugs[2, 0] = round(0.6 + (i/10), 1)

        # Determine the eigenvalues
        eigenvalues = np.linalg.eigvals(matrix_drugs)

        # Make a dataframe
        column_names = ['Generations no drug', 'Generations drug', 'MM fraction']
        df_holliday = pd.DataFrame(columns=column_names)
        df_holliday = pd.DataFrame(columns=column_names)

        # Loop over al the t_step values for drug dministration and drug holidays
        for t_steps_no_drug in range(2, 22):

            for t_steps_drug in range(2, 22):

                freq_tumour = mimimal_tumour_frac_t_steps(t_steps_drug,
                                t_steps_no_drug, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, matrix_no_drugs, matrix_drugs)

                # Add results to the dataframe
                new_row_df = pd.DataFrame([{'Generations no drug': \
                    int(t_steps_no_drug), 'Generations drug': int(t_steps_drug),
                    'MM fraction': float(freq_tumour)}])
                df_holliday = pd.concat([df_holliday, new_row_df], ignore_index=True)

        # Find the drug administration and holiday period causing the lowest MM
        # fraction
        min_index = df_holliday['MM fraction'].idxmin()
        g_no_drug_min = df_holliday.loc[min_index, 'Generations no drug']
        g_drug_min = df_holliday.loc[min_index, 'Generations drug']
        frac_min = df_holliday.loc[min_index, 'MM fraction']

        # Add data to a dataframe
        new_row_df = pd.DataFrame([{'bOC,MMd': round(0.6 + (i/10), 1),
        'Eigenvalue 1': eigenvalues[0], 'Eigenvalue 2': eigenvalues[1],
        'Eigenvalue 3': eigenvalues[2], 'Eigenvalue 4': eigenvalues[3],
        'period H': g_no_drug_min, 'period A': g_drug_min, 'MM fraction': frac_min}])
        df_eigenvalues = pd.concat([df_eigenvalues, new_row_df], ignore_index=True)

        # Add data to a dataframe and discard the imaginary part to make it a float
        new_row_df = pd.DataFrame([{'bMMd,MMd & bMMr,MMr': round(0.6 + (i/10), 1),
        'Eigenvalue 1':float(eigenvalues[0]), 'Eigenvalue 2': float(eigenvalues[1]),
        'Eigenvalue 3': float(eigenvalues[2]), 'Eigenvalue 4': float(eigenvalues[3]),
        'period H': g_no_drug_min, 'period A': g_drug_min, 'MM fraction': frac_min}])
        df_eigenvalues_float = pd.concat([df_eigenvalues_float, new_row_df],
                                                                ignore_index=True)

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 1
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 1'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 1 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 1'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 1 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 1'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 1 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 2
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 2'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 2 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 2'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 2 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 2'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 2 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 3
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 3'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 3 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 3'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 3 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 3'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 3 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 4
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 4'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 4 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 4'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 4 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 4'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 4 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Save the data
    save_dataframe(df_eigenvalues, 'df_eigenvalues_bOCMMd.csv',
                                             r'..\data\data_own_model_fractions')

def Dataframe_bMMdMMd_bMMrMMr_eigenvalues():
    """ Function that makes a table of the eigenvalues of the interaction matrix,
    MM fraction and the best holiday (H) and administration (A) period for
    different bMMd,MMd and bMMr,MMr values."""

    # Make a dataframe
    column_names = ['bMMd,MMd & bMMr,MMr', 'Eigenvalue 1', 'Eigenvalue 2',
        'Eigenvalue 3', 'Eigenvalue 4', 'period H', 'period A', 'MM fraction']
    df_eigenvalues = pd.DataFrame(columns=column_names)
    df_eigenvalues_float = pd.DataFrame(columns=column_names)

    for i in range(6):
        # Set initial parameter values
        N = 50
        cMMr = 1.3
        cMMd = 1.2
        cOB = 0.8
        cOC = 1
        xOC = 0.2
        xOB = 0.3
        xMMd = 0.2
        xMMr = 0.3

        # Payoff matrix when no drugs are present
        matrix_no_drugs = np.array([
            [0.0, 1.6, 2.2, 1.9],
            [1.0, 0.0, -0.5, -0.5],
            [2.2, 0.0, 0.2, 0.0],
            [1.9, 0.0, -0.8, 0.2]])

        # Payoff matrix when only GF inhibitor drugs are present
        matrix_drugs = np.array([
            [0.0, 1.6, 2.2, 1.9],
            [1.0, 0.0, -0.5, -0.5],
            [0.7, 0.0, 0.2, 0.0],
            [1.9, 0, -0.8, 0.2]])

        # Change the interaction values
        matrix_drugs[2, 2] = round(0.1 + (i/5), 1)
        matrix_drugs[3, 3] = round(0.1 + (i/5), 1)
        matrix_no_drugs[2, 2] = round(0.1 + (i/5), 1)
        matrix_no_drugs[3, 3] = round(0.1 + (i/5), 1)

        # Determine the eigenvalues
        eigenvalues = np.linalg.eigvals(matrix_no_drugs)

        # Make a dataframe
        column_names = ['Generations no drug', 'Generations drug', 'MM fraction']
        df_holliday = pd.DataFrame(columns=column_names)

        # Loop over al the t_step values for drug dministration and drug holidays
        for t_steps_no_drug in range(2, 22):

            for t_steps_drug in range(2, 22):
                freq_tumour = mimimal_tumour_frac_t_steps(t_steps_drug,
                                t_steps_no_drug, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, matrix_no_drugs, matrix_drugs)

                # Add results to the dataframe
                new_row_df = pd.DataFrame([{'Generations no drug': \
                    int(t_steps_no_drug), 'Generations drug': int(t_steps_drug),
                    'MM fraction': float(freq_tumour)}])
                df_holliday = pd.concat([df_holliday, new_row_df], ignore_index=True)

        # Find the drug administration and holiday period causing the lowest MM
        # fraction
        min_index = df_holliday['MM fraction'].idxmin()
        g_no_drug_min = df_holliday.loc[min_index, 'Generations no drug']
        g_drug_min = df_holliday.loc[min_index, 'Generations drug']
        frac_min = df_holliday.loc[min_index, 'MM fraction']

        # Add data to a dataframe
        new_row_df = pd.DataFrame([{'bMMd,MMd & bMMr,MMr':  round(0.1 + (i/5), 1),
        'Eigenvalue 1': eigenvalues[0], 'Eigenvalue 2': eigenvalues[1],
        'Eigenvalue 3': eigenvalues[2], 'Eigenvalue 4': eigenvalues[3],
        'period H': g_no_drug_min, 'period A': g_drug_min, 'MM fraction': frac_min}])
        df_eigenvalues = pd.concat([df_eigenvalues, new_row_df], ignore_index=True)

        # Add data to a dataframe and discard the imaginary part to make it a float
        new_row_df = pd.DataFrame([{'bMMd,MMd & bMMr,MMr':  round(0.1 + (i/5), 1),
        'Eigenvalue 1':float(eigenvalues[0]), 'Eigenvalue 2': float(eigenvalues[1]),
        'Eigenvalue 3': float(eigenvalues[2]), 'Eigenvalue 4': float(eigenvalues[3]),
        'period H': g_no_drug_min, 'period A': g_drug_min, 'MM fraction': frac_min}])
        df_eigenvalues_float = pd.concat([df_eigenvalues_float, new_row_df],
                                                                ignore_index=True)

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 1
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 1'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 1 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 1'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 1 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 1'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 1 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 2
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 2'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 2 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 2'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 2 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 2'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 2 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 3
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 3'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 3 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 3'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 3 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 3'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 3 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")

    # Calculate Spearman correlation coefficients and p-values with eigenvalue 4
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 4'], df_eigenvalues_float['period H'])
    print(f"""Eigenvalue 4 and holiday period: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 4'], df_eigenvalues_float['period A'])
    print(f"""Eigenvalue 4 and administration period: p-value = {p_value},
    correlation coefficient = {correlation_coefficient}""")
    correlation_coefficient, p_value = spearmanr(df_eigenvalues_float[\
                            'Eigenvalue 4'], df_eigenvalues_float['MM fraction'])
    print(f"""Eigenvalue 4 and MM fraction: p-value = {p_value}, correlation
    coefficient = {correlation_coefficient}""")


    # Save the data
    save_dataframe(df_eigenvalues, 'df_eigenvalues_bMMdMMd_bMMrMMr.csv',
                                            r'..\data\data_own_model_fractions')

if __name__ == "__main__":
    main()