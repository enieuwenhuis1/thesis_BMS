"""
Author:       Eva Nieuwenhuis
Student ID:   13717405
Group:        Biosystems Data Analysis Group
Course:       Bachelor project biomedical science, UvA

Description:  Code with the model that simulates the dynamics in the multiple
              myeloma (MM) microenvironment with four cell types: drug-sensitive
              MM cells (MMd), resistant MM cells (MMr), osteoblasts (OB) and
              osteoclasts (OC). The model has collective interactions and linear
              benefits and is made in the framework of evolutionary game theory.
              In this model, there is looked at the fraction dynamics of the four
              cell types during different IH administration methods. The IHs do
              not only influence on the MMd but also the OB and OC.


Example interaction matrix:
M = np.array([
         Foc     Fob   Fmmd   Fmmr
    OC  [b1,1,  b2,1,  b3,1,  b4,1],
    OB  [b1,2,  b2,2,  b3,2,  b4,2],
    MMd [b1,3,  b2,3,  b3,3,  b4,3],
    MMr [b1,4,  b2,4,  b3,4,  b4,4]])
"""

# Import the needed libraries
import math
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import csv
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D
import doctest

def main():
    # Do doc tests
    doctest.testmod()

    # Make a figure showing the cell fraction dynamics by traditional therapy and
    # by adaptive therapy (original situation)
    list_t_steps_drug = [10, 10, 10]
    Figure_continuous_MTD_vs_AT_a_h(13, list_t_steps_drug)

    # Make a figure showing the cell fraction dynamics by traditional therapy and
    # by adaptive therapy for shorter holiday and administration periods compared
    # to the original situation
    list_t_steps_drug = [5, 5, 5]
    Figure_continuous_MTD_vs_AT_short_a_h(20, list_t_steps_drug)

    # Make a figure showing the cell fraction dynamics by traditional therapy
    # and by adaptive therapy for weaker IHs compared to the original situation
    list_t_steps_drug = [10, 10, 10]
    Figure_continuous_MTD_vs_AT_weak_a_h(12, list_t_steps_drug)

    # Make a figure showing the cell fraction dynamics by traditional therapy and
    # by adaptive therapy for shorter holiday and administration periods and
    # weaker IHs compared to the original situation
    list_t_steps_drug = [5, 5, 5]
    Figure_continuous_MTD_vs_AT_realistic(18, list_t_steps_drug)

    # Make a figure showing the cell fraction dynamics by traditional therapy and
    # by adaptive therapy whereby the OB-OC equilibrium gets restored
    list_t_steps_drug = [10, 10, 10]
    Figure_continuous_MTD_vs_AT_OB_a_h(9, list_t_steps_drug)

    # Make a 3D figure showthing the effect of different drug holiday and
    # administration periods
    Figure_3D_MM_frac_IH_add_and_holiday()

    # Make a figure that shows the MM fraction for different bOC,MMd values
    Figure_best_b_OC_MMd()

    # Make a figure that shows the MM fraction for different WMMd IH values
    Figure_best_WMMd_IH()

    # Make a 3D figure showing the effect of different WMMd and MMd GF IH
    # strengths
    Figure_3D_MM_frac_MMd_IH_strength()

    # Make a figure that shows the cell fraction dynamics and fitness
    Figure_frac_fitness_dynamics()

    # Make line plots showing the dynamics when the IH administration is longer
    # than the holiday and one it is the other way around.
    list_t_steps_drug = [5, 8]
    list_t_steps_no_drug = [8, 5]
    list_n_steps = [18, 18]
    Figure_duration_A_h_MMd_IH(list_n_steps, list_t_steps_drug,
                                                        list_t_steps_no_drug)

    # Make a figure of the fraction dynamics whereby there is a limit for the MMd
    # and MMr fraction
    Figure_AT_MMd_MMr_limit(0.3, 0.15)


def fitness_WOC(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix):
    """
    Function that calculates the fitness of an osteoclast in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of individuals within the interaction range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
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
    b1_1 = matrix[0, 0]
    b2_1 = matrix[0, 1]
    b3_1 = matrix[0, 2]
    b4_1 = matrix[0, 3]

    # Calculate the fitness value
    WOC = (b1_1*xOC*cOC + b2_1*xOB*cOB + b3_1*xMMd*cMMd + b4_1*xMMr*cMMr) \
                                                                *(N - 1)/N - cOC
    return WOC

def fitness_WOB(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix):
    """
    Function that calculates the fitness of an osteoblast in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of individuals within the interaction range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
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
    b1_2 = matrix[1, 0]
    b2_2 = matrix[1, 1]
    b3_2 = matrix[1, 2]
    b4_2 = matrix[1, 3]

    # Calculate the fitness value
    WOB = (b1_2*xOC*cOC + b2_2*xOB*cOB + b3_2*xMMd*cMMd + b4_2* xMMr*cMMr) \
                                                                *(N - 1)/N - cOB
    return WOB

def fitness_WMMd(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix,
                                                            WMMd_inhibitor = 0):
    """
    Function that calculates the fitness of a drug-senstive MM cell in a
    population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of individuals within the interaction range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

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
    b1_3 = matrix[2, 0]
    b2_3 = matrix[2, 1]
    b3_3 = matrix[2, 2]
    b4_3 = matrix[2, 3]

    # Calculate the fitness value
    WMMd = (b1_3*xOC*cOC + b2_3*xOB*cOB + b3_3*xMMd*cMMd + b4_3* xMMr*cMMr - \
                                                WMMd_inhibitor)*(N - 1)/N - cMMd
    return WMMd

def fitness_WMMr(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, matrix):
    """
    Function that calculates the fitness of a resistant MM cell in a population.

    Parameters:
    -----------
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of individuals within the interaction range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
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
    b1_4 = matrix[3, 0]
    b2_4 = matrix[3, 1]
    b3_4 = matrix[3, 2]
    b4_4 = matrix[3, 3]

    # Calculate the fitness value
    WMMr = (b1_4*xOC*cOC + b2_4*xOB*cOB + b3_4*xMMd*cMMd + b4_4* xMMr*cMMr)* \
                                                                (N - 1)/N - cMMr
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
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

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


def dynamics_MMd_MMr_limits(time_IH, time_end, upper_limit_MMd, upper_limit_MMr,
                xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, cOC_IH, cOB_IH,
                matrix_no_drugs, matrix_drugs, WMMd_inhibitor = 0):
    """Function that determines the number dynamics. It ensures that the MMr
    number and MMd fraction do not become too high.

    Parameters:
    -----------
    time_IH: Int
        fraction of generations before the therapy start
    time_end: Int
        The last generation for which the fractions have to be calculated
    upper_limit_MMd: Int
        The maximum fraction of MMd, when reached the IH administration starts
    upper_limit_MMr: Int
        The maximum fraction of MMr, when reached the IH administration stops
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of individuals within the interaction range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix_no_drugs: Numpy.ndarray
        4x4 matrix containing the interaction factors when no IHs are given.
    matrix_drugs: Numpy.ndarray
        4x4 matrix containing the interaction factors when IHs are given.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    df_fractions: DataFrame
        The dataframe with the fraction per cell type over the time
    average_a_duration: Float
        The average administration duration
    average_h_duration: Float
        The average holiday duration
    """
    # Create a dataframe and lists
    df_fractions = pd.DataFrame(columns = ['Generation', 'xOC', 'xOB', 'xMMd',
                                                        'xMMr', 'total xMM'])
    duration_holiday = []
    duration_administration = []

    # Set the start values
    times_holiday = 0
    times_administration = 0
    duration = 0
    x = int(1)
    t = np.linspace(0, time_IH, time_IH)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_drugs)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
        'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_fractions = combine_dataframes(df_fractions, df)

    # Calculate the fraction of generations the therapy is given
    time_step_t = time_end - time_IH

    # Loop over the generations
    for time_step in range(time_step_t):

        # Determine the start fractions
        xOC = df_fractions['xOC'].iloc[-1]
        xOB = df_fractions['xOB'].iloc[-1]
        xMMd = df_fractions['xMMd'].iloc[-1]
        xMMr = df_fractions['xMMr'].iloc[-1]

        # If x = 1 add IHs and if x = 0 add no IHs
        if x == 1:
            # Determine the fitness values
            WOC = fitness_WOC(xOC, xOB, xMMd, xMMr, N, cOC_IH, cOB_IH, cMMd,
                                                        cMMr, matrix_drugs)
            WOB = fitness_WOB(xOC, xOB, xMMd, xMMr,  N, cOC_IH, cOB_IH, cMMd,
                                                            cMMr, matrix_drugs)
            WMMd = fitness_WMMd(xOC, xOB, xMMd, xMMr, N, cOC_IH, cOB_IH, cMMd,
                                            cMMr, matrix_drugs, WMMd_inhibitor)
            WMMr = fitness_WMMr(xOC, xOB, xMMd, xMMr, N, cOC_IH, cOB_IH, cMMd,
                                                            cMMr, matrix_drugs)

            # Determine the average fitness
            W_average = xOC * WOC + xOB * WOB + xMMd * WMMd + xMMr * WMMr

            # Determine the new fractions based on replicator dynamics
            xOC_change = xOC * (WOC - W_average)
            xOB_change = xOB * (WOB - W_average)
            xMMd_change = xMMd * (WMMd - W_average)
            xMMr_change = xMMr * (WMMr - W_average)

        if x == 0:
            # Determine the fitness values
            WOC = fitness_WOC(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                                                                matrix_no_drugs)
            WOB = fitness_WOB(xOC, xOB, xMMd, xMMr,  N, cOC, cOB, cMMd, cMMr,
                                                                matrix_no_drugs)
            WMMd = fitness_WMMd(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                                                                matrix_no_drugs)
            WMMr = fitness_WMMr(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                                                                matrix_no_drugs)

            # Determine the average fitness
            W_average = xOC * WOC + xOB * WOB + xMMd * WMMd + xMMr * WMMr

            # Determine the new fractions based on replicator dynamics
            xOC_change = xOC * (WOC - W_average)
            xOB_change = xOB * (WOB - W_average)
            xMMd_change = xMMd * (WMMd - W_average)
            xMMr_change = xMMr * (WMMr - W_average)

        # Calculate the new cell fractions
        xOC = xOC + xOC_change
        xOB = xOB + xOB_change
        xMMd = xMMd + xMMd_change
        xMMr = xMMr + xMMr_change
        xMMt = xMMd + xMMr

        # If there are too many MMr stop drug administration
        if xMMr > upper_limit_MMr:

            if x == int(1):
                duration_administration.append(duration)
                times_administration += 1
                duration = 0

            x = int(0)

        # If there are too many MMd stop drug holiday
        if xMMd > upper_limit_MMd:

            if x == int(0):
                duration_holiday.append(duration)
                times_holiday += 1
                duration = 0
            x = int(1)

        # Add results to the dataframe
        new_row_df = pd.DataFrame([{'Generation': time_IH+time_step, 'xOC': xOC,
                'xOB': xOB, 'xMMd': xMMd, 'xMMr': xMMr, 'total xMM': xMMt}])
        df_fractions = combine_dataframes(df_fractions, new_row_df)

        # Add one to the duration
        duration += 1

    # Calculate average administration and holiday duration
    average_a_duration = sum(duration_administration) / times_administration
    average_h_duration = sum(duration_holiday) / times_holiday

    return df_fractions, average_a_duration, average_h_duration


def frac_to_fitness_values(dataframe_fractions, N, cOC, cOB, cMMd, cMMr, matrix,
                                                            WMMd_inhibitor = 0):
    """Function that determines the fitness values of the OC, OB, MMd and MMr
    based on their fractions on every time point. It also calculates the average
    fitness.

    Parameters:
    -----------
    dataframe_fractions: DataFrame
        Dataframe with the fractions of the OB, OC MMd and MMr on every
        timepoint.
    N: Int
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    dataframe_fitness: DataFrame
        A dataframe with the fitness values of the OB, OC, MMd and MMr and
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

def combine_dataframes(df_1, df_2):
    """ Function that combines two datafranes in on dataframe

    Parameters:
    -----------
    df_1: DataFrame
        The first dataframe containing the collected data.
    df_2: DataFrame
        The second dataframe containing the collected data.

    Returns:
    --------
    combined_df: DataFrame
        Dataframe that is a combination of the two dataframes
    """
    # Check if the dataframes are empty
    if df_1.empty or df_2.empty:

        # Return the dataframe that is not empty
        combined_df = df_1 if not df_1.empty else df_2

    else:
        # Delete the NA columns
        df_1 = df_1.dropna(axis=1, how='all')
        df_2 = df_2.dropna(axis=1, how='all')

        # Combine the dataframes
        combined_df =  pd.concat([df_1, df_2], ignore_index=True)

    return(combined_df)

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

def save_Figure(figure, file_name, folder_path):
    """Save the Figure to a specific folder.

    Parameters:
    -----------
    figure: Matplotlib Figure
        Figure object that needs to be saved.
    file_name: String
        The name for the plot.
    folder_path: String:
        Path to the folder where the data will be saved.
    """
    os.makedirs(folder_path, exist_ok=True)
    figure.savefig(os.path.join(folder_path, file_name))


def make_part_df(dataframe, start_time, time, N, cOC, cOB, cMMd, cMMr, matrix,
            WMMd_inhibitor = 0):
    """ Function that adds the cell numbers over a specified time to a given
    dataframe

    Parameters:
    -----------
    dataframe: DataFrame
        The dataframe to which the extra data should be added.
    start_time: Int
        The last generation in the current dataframe
    time: Int
        The time the cell number should be calculated
    N: Int
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    matrix: Numpy.ndarray
        4x4 matrix containing the interaction factors
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    df_total: Dataframe
        Dataframe with the extra nOC, nOB, nMMd and nMMr values
    """
    # Determine the start fraction values
    xOC = dataframe['xOC'].iloc[-1]
    xOB = dataframe['xOB'].iloc[-1]
    xMMd = dataframe['xMMd'].iloc[-1]
    xMMr = dataframe['xMMr'].iloc[-1]

    # Set start parameter values
    t = np.linspace(start_time, start_time+ time, int(time))
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
        'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Add dataframe to total dataframe
    df_total = combine_dataframes(dataframe, df)
    df_total.reset_index(drop=True, inplace=True)

    return df_total

def switch_dataframe(time_start_drugs, n_switches, t_steps_drug, t_steps_no_drug,
                xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, cOC_IH, cOB_IH,
                matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor = 0):
    """ Function that makes a dataframe of the xOC, xOB, xMMd and xMMr values
    over time for a given time of drug holiday and administration periods.

    Parameters:
    -----------
    time_start_drugs: Int
        The generation after which the inhibitors will be administared.
    n_switches: Int
        The fraction of switches between giving drugs and not giving drugs.
    t_steps_drug: Int
        The fraction of generations drugs are administared.
    t_steps_no_drug: Int
        The fraction of generations drugs are not administared.
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter MMd.
    cMMr: Float
        Cost parameter MMr.
    cOC_IH: Float
        Cost parameter OC when a IH is administered.
    cOB_IH: Float
        Cost parameter OB when a IH is administered.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are
                                                                administered.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are administered.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    df_total_switch: DataFrame
        Dataframe with the xOC, xOB, xMMd and xMMr values over time.
    """
    # Set initial values
    x = 0
    time = 0
    df_total_switch = pd.DataFrame()
    t_steps = time_start_drugs
    t = np.linspace(0, t_steps, t_steps*2)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_total_switch = pd.DataFrame({'Generation': t, 'xOC':y[:, 0], 'xOB':y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Increase the time
    time += t_steps

    # Perform a fraction of switches
    for i in range(n_switches):

        # If x = 0 make sure the MMd is inhibited
        if x == 0:
            df_total_switch = make_part_df(df_total_switch, time, t_steps_drug,
                    N, cOC_IH, cOB_IH, cMMd, cMMr, matrix_GF_IH, WMMd_inhibitor)

            # Change the x and time value
            x = 1
            time += t_steps_drug

        # If x = 1 make sure the MMd is not inhibited
        else:
            df_total_switch = make_part_df(df_total_switch, time, t_steps_no_drug,
                                    N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

            # Change the x and time value
            x = 0
            time += t_steps_no_drug

    return df_total_switch


def continuous_add_IH_df(time_start_drugs, end_generation, xOC, xOB, xMMd, xMMr,
        N, cOC, cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH,
        WMMd_inhibitor = 0):
    """ Function that makes a dataframe of the cell type fractions when the IHs
    are administered continuously.

    Parameters:
    -----------
    time_start_drugs: Int
        The generation after which the inhibitors will get administared
    end_generation: Int
        The last generation for which the fractions have to be calculated
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the MMd.
    xMMr: Float
        Fraction of the MMr.
    N: Int
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    cOC_IH: Float
        Cost parameter OC when a IH is administered.
    cOB_IH: Float
        Cost parameter OB when a IH is administered.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are
                                                                administrated.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are
                                                                administrated.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    df_total: DataFrame
        The dataframe with the cell fractions when IHs are continiously
                                                                administered.
    """
    t = np.linspace(0, time_start_drugs, time_start_drugs)
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

    t = np.linspace(time_start_drugs, end_generation, 120)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC_IH, cOB_IH, cMMd, cMMr, matrix_GF_IH, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2 = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total xMM': y[:, 3]+ y[:, 2]})

    # Combine the dataframes
    df_total = combine_dataframes(df_1, df_2)

    return df_total

def minimal_tumour_frac_t_steps(t_steps_drug, t_steps_no_drug, xOC, xOB, xMMd,
                            xMMr, N, cOC, cOB, cMMd, cMMr, cOC_IH, cOB_IH,
                            matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor = 0):
    """ Function that makes a dataframe of the xOC, xOB, xMMd and xMMr values
    over time for a given time of a drug holiday.

    Parameters:
    -----------
    t_steps_drug: Int
        The fraction of generations drugs are administared.
    t_steps_no_drug: Int
        The fraction of generations drugs are not administared.
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMr: Float
        Fraction of the MMr.
    xMMd: Float
        Fraction of the MMd.
    N: Int
        fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    cOC_IH: Float
        Cost parameter OC when a IH is administered.
    cOB_IH: Float
        Cost parameter OB when a IH is administered.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are
                                                                administered.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are administered.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    average_MM_fraction: Float
        The average MM fraction in the equilibrium.

    Example:
    -----------
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
    >>> minimal_tumour_frac_t_steps(5, 5, 0.2, 0.3, 0.2, 0.3, 10, 0.3, 0.2, 0.3,
    ...                         0.5, 0.4, 0.2, matrix_no_GF_IH, matrix_no_GF_IH)
    4.533166876036014e-11
    """
    # Deteremine the fraction of switches
    time_step = (t_steps_drug + t_steps_no_drug) / 2
    n_switches = int((110 // time_step) -1)

    # Create a dataframe of the fractions
    df = switch_dataframe(15, n_switches, t_steps_drug, t_steps_no_drug, xOC, xOB,
                            xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, cOC_IH, cOB_IH,
                             matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor)

    # Determine the average MM fraction in the last period with and without drugs
    last_MM_fractions = df['total xMM'].tail(int(time_step *2))
    average_MM_fraction = last_MM_fractions.sum() / (int(time_step*2))

    return float(average_MM_fraction)


def dataframe_3D_plot(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr, cOC_IH,
            cOB_IH, matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor = 0):
    """ Function that create a dataframe with the average MM fraction for
    different IH administration and holiday durations

    Parameters:
    -----------
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMr: Float
        Fraction of the MMr.
    xMMd: Float
        Fraction of the MMd.
    N: Int
        fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMr: Float
        Cost parameter MMr.
    cMMd: Float
        Cost parameter MMd.
    cOC_IH: Float
        Cost parameter OC when a IH is administered.
    cOB_IH: Float
        Cost parameter OB when a IH is administered.
    matrix_no_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when no GF IH are
                                                                administered.
    matrix_GF_IH: Numpy.ndarray
        4x4 matrix containing the interaction factors when GF IH are administered.
    WMMd_inhibitor: Float
        The effect of a drug on the MMd fitness.

    Returns:
    --------
    df_MM_frac: DataFrame
        The dataframe with the average MM fraction for different IH holiday
        and administration durations
    """
    # Make a dataframe
    column_names = ['Generations no drug', 'Generations drug', 'MM fraction']
    df_MM_frac = pd.DataFrame(columns=column_names)

    # Loop over all the t_step values for drug administration and drug holidays
    for t_steps_no_drug in range(2, 22):

        for t_steps_drug in range(2, 22):
            frac_tumour = minimal_tumour_frac_t_steps(t_steps_drug,
                t_steps_no_drug, xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH, WMMd_inhibitor)

            # Add results to the dataframe
            new_row_df = pd.DataFrame([{'Generations no drug': \
                    int(t_steps_no_drug), 'Generations drug': int(t_steps_drug),
                                         'MM fraction': float(frac_tumour)}])
            df_MM_frac = combine_dataframes(df_MM_frac, new_row_df)

    return(df_MM_frac)

def x_y_z_axis_values_3d_plot(dataframe, name):
    """ Function that determines the x, y and z axis values from the given
    dataframe. It also prints the administration and holiday duration leading
    to the lowest total MM fraction in the equilibrium

    Parameters:
    -----------
    Dataframe: DataFrame
        The dataframe with the generated data
    name: String
        The name of the administered IH(s)

    Returns:
    --------
    X_values: Numpy.ndarray
        Array with the values for the x-axis
    Y_values: Numpy.ndarray
        Array with the values for the y-axis
    Z_values: Numpy.ndarray
        Array with the values for the z-axis
    """

    # Find the drug administration and holiday period causing the lowest MM
    # fraction
    min_index =  dataframe['MM fraction'].idxmin()
    g_no_drug_min = dataframe.loc[min_index, 'Generations no drug']
    g_drug_min = dataframe.loc[min_index, 'Generations drug']
    frac_min = dataframe.loc[min_index, 'MM fraction']

    print(f"""Lowest MM fraction: {frac_min}-> MMd {name} holidays are
            {g_no_drug_min} generations and MMd {name} administrations
            are {g_drug_min} generations""")

    # Avoid errors because of the wrong datatype
    dataframe['Generations no drug'] = pd.to_numeric(dataframe[\
                                        'Generations no drug'], errors='coerce')
    dataframe['Generations drug'] = pd.to_numeric(dataframe[\
                                        'Generations drug'],errors='coerce')
    dataframe['MM fraction'] = pd.to_numeric(dataframe['MM fraction'],
                                                            errors='coerce')

    # Make a meshgrid for the plot
    X_values = dataframe['Generations no drug'].unique()
    Y_values = dataframe['Generations drug'].unique()
    X_values, Y_values = np.meshgrid(X_values, Y_values)
    Z_values = np.zeros((20, 20))

    # Fill the 2D array with the MM fraction values by looping over each row
    for index, row in dataframe.iterrows():
        i = int(row.iloc[0]) - 2
        j = int(row.iloc[1]) - 2
        Z_values[j, i] = row.iloc[2]

    return (X_values, Y_values, Z_values)

def avarage_MMr_MMd_nr(dataframe, time, therapy):
    """ Function that calculates the average MMd and MMr number

    Parameters:
    -----------
    dataframe: DataFrame
        The dataframe containing the MMd and MMr numbers over time
    time: Int
        The time over which the average MMd and MMr number should be calculated
    therapy: String
        The kind of therapy used
    """

    last_MMd_fractions = dataframe['xMMd'].tail(int(time))
    average_MMd_fraction = round(last_MMd_fractions.sum() / time, 2)
    last_MMr_fractions = dataframe['xMMr'].tail(int(time))
    average_MMr_fraction = round(last_MMr_fractions.sum() / time, 2)
    print(f'{therapy}: xMMd =',average_MMd_fraction,
                                        'and xMMr =', average_MMr_fraction)

def minimal_tumour_frac_b_OC_MMd(b_OC_MMd, xOC, xOB, xMMd, xMMr, N, cOC, cOB,
                        cMMd, cMMr, cOC_IH, cOB_IH, matrix, t, b_OC_MMd_array):
    """Function that determines the fraction of the population being MM for a
    specific b_OC_MMd value.

    Parameters:
    -----------
    b_OC_MMd: Float
        Interaction value that gives the effect of the GFs of OC on MMd.
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the drug-sensitive MM cells.
    xMMr: Float
        Fraction of the resistant MM cells.
    N: Int
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter drug-sensitive MM cells.
    cMMr: Float
        Cost parameter resistant MM cells.
    cOC_IH: Float
        Cost parameter OC when a IH is administered.
    cOB_IH: Float
        Cost parameter OB when a IH is administered.
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
    """
    # Change b_OC_MMd to a float if it is an array
    if b_OC_MMd_array == True:
        b_OC_MMd = b_OC_MMd[0]

    # Change the b_OC_MM value to the specified value
    matrix[2, 0]= b_OC_MMd

    # Set the initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC_IH, cOB_IH, cMMd, cMMr, matrix)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total_MM': y[:, 3]+ y[:, 2]})

    # Determine the total MM fraction
    last_MM_fraction = df['total_MM'].iloc[-1]

    return float(last_MM_fraction)

"""Determine the best drug effect value for high and low cOB and cOC values"""
def minimal_tumour_frac_WMMd_IH(WMMd_inhibitor, xOC, xOB, xMMd, xMMr, N, cOC,
            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix, t, WMMd_inhibitor_array):
    """Function that determines the fraction of the population being MM for a
    specific WMMd drug inhibitor value.

    Parameters:
    -----------
    WMMd_inhibitor: Float
        Streght of the drugs that inhibits the MMd fitness.
    xOC: Float
        Fraction of OC.
    xOB: Float
        Fraction of OB.
    xMMd: Float
        Fraction of the drug-sensitive MM cells.
    xMMr: Float
        Fraction of the resistant MM cells.
    N: Int
        Fraction of cells in the difussion range.
    cOC: Float
        Cost parameter OC.
    cOB: Float
        Cost parameter OB.
    cMMd: Float
        Cost parameter drug-sensitive MM cells.
    cMMr: Float
        Cost parameter resistant MM cells.
    cOC_IH: Float
        Cost parameter OC when a IH is administered.
    cOB_IH: Float
        Cost parameter OB when a IH is administered.
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
    """
    # Determine if WMMd_inhibitor is an array
    if WMMd_inhibitor_array == True:
        WMMd_inhibitor = WMMd_inhibitor[0]

    # Set initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC_IH, cOB_IH, cMMd, cMMr, matrix, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df = pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': y[:, 1],
                'xMMd': y[:, 2], 'xMMr': y[:, 3], 'total_MM': y[:, 3]+ y[:, 2]})

    # Determine the total MM fraction
    last_MM_fraction = df['total_MM'].iloc[-1]

    return float(last_MM_fraction)

""" Figure to determine the best WMMd IH value """
def Figure_best_WMMd_IH():
    """ Function that shows the effect of different OB and OC cost values for
    different WMMd drug inhibitor values. It also determines the WMMd IH value
    causing the lowest total MM fraction."""
    # Set start values
    N = 50
    cMMr = 1.3
    cMMd = 1.2
    cOB = 0.8
    cOC = 1.0
    xOC = 0.4
    xOB = 0.3
    xMMd = 0.2
    xMMr = 0.1

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix
    matrix = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.89, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    t = np.linspace(0, 100, 100)

    # Make a dictionary
    dict_frac_tumour = {}

    # Loop over the different WMMd_inhibitor values
    for WMMd_inhibitor in range(3000):
        WMMd_inhibitor = WMMd_inhibitor/1000
        frac_tumour = minimal_tumour_frac_WMMd_IH(WMMd_inhibitor, xOC, xOB, xMMd,
                xMMr, N, cOC, cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix, t, False)
        dict_frac_tumour[WMMd_inhibitor] = frac_tumour

    # Save the data
    save_dictionary(dict_frac_tumour,
            r'..\data\data_model_frac_IH_inf\dict_cell_frac_IH_WMMd_IH.csv')

    # Retrieve the optimal value
    min_value = min(dict_frac_tumour.values())
    min_keys = [key for key, value in dict_frac_tumour.items() if value == \
                                                                    min_value]

    print("Optimal value for the WMMd IH by high OB and OC cost values:",
                float(min_keys[0]), ', gives tumour fraction:',min_value)


    # Make lists of the keys and the values
    keys = list(dict_frac_tumour.keys())
    values = list(dict_frac_tumour.values())

    # Make a plot
    plt.plot(keys, values, color='purple')
    plt.title(r"""MM fraction for various $W_{MMd}$ IH strengths""")
    plt.xlabel(r' $W_{MMd}$ strength')
    plt.ylabel('MM fraction')
    plt.grid(True)
    save_Figure(plt, 'line_plot_cell_frac_IH_change_WMMd_IH',
                                 r'..\visualisation\results_model_frac_IH_inf')
    plt.show()


""" Figure to determine the best b_OC_MMd value """
def Figure_best_b_OC_MMd():
    """ Function that makes a Figure that shows the total MM fraction for
    different b_OC_MMd values. It also determines the b_OC_MMd value causing the
    lowest total MM fraction"""

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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix
    matrix = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.89, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    t = np.linspace(0, 100, 100)
    b_OC_MMd_start = 1.5

    # Make a dictionary
    dict_frac_tumour_GF = {}

    # Loop over all the b_OC_MMd values
    for b_OC_MMd in range(3000):
        b_OC_MMd = b_OC_MMd/1000

        # Determine the total MM fraction
        frac_tumour = minimal_tumour_frac_b_OC_MMd(b_OC_MMd, xOC, xOB, xMMd,
                xMMr, N, cOC, cOB, cMMd, cMMr, cOB_IH, cOC_IH, matrix, t, False)
        dict_frac_tumour_GF[b_OC_MMd] = frac_tumour

    # Save the data
    save_dictionary(dict_frac_tumour_GF,
             r'..\data\data_model_frac_IH_inf\dict_cell_frac_IH_b_OC_MMd.csv')

    # Retrieve the optimal value
    min_value = min(dict_frac_tumour_GF.values())
    min_keys = [key for key, value in dict_frac_tumour_GF.items() if value ==\
                                                                    min_value]

    print("Optimal value for b_OC_MMd:", float(min_keys[0]),
                                            'gives tumour fraction:', min_value)

    # Make a list of the keys and one of the values
    b_OC_MMd_values = list(dict_frac_tumour_GF.keys())
    MM_fractions = list(dict_frac_tumour_GF.values())

    # Create the plot
    plt.plot(b_OC_MMd_values, MM_fractions, linestyle='-')
    plt.xlabel(r'$b_{OC, MMd}$ value ')
    plt.ylabel(r'Total MM fraction')
    plt.title(r'MM fraction for different $b_{OC, MMd}$ values')
    plt.grid(True)
    save_Figure(plt, 'line_plot_cell_frac_IH_change_b_OC_MMd',
                                r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

""" Figure to determine the difference between traditional and adaptive therapy
(original situation)"""
def Figure_continuous_MTD_vs_AT_a_h(n_switches, t_steps_drug):
    """ Function that makes a figure with 6 subplots showing the cell type
    fraction dynamics by traditional therapy (continuous MTD) and adaptive
    therapy.

    Parameters:
    -----------
    n_switches: Int
        The fraction of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the fraction of time steps drugs are administared and the
        breaks are for the different Figures.
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [0.5, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [1.2, 0.0, 0.2, 0.0],
        [1.9, 0.0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.6

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.45

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF = switch_dataframe(15, n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMd = switch_dataframe(15, n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb = switch_dataframe(15, n_switches, t_steps_drug[2],
                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_IH_comb,
                WMMd_inhibitor_comb)

    # Make dataframes for continiously administration
    df_total_GF = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_WMMd = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                            matrix_no_GF_IH, WMMd_inhibitor)
    df_total_comb = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                            matrix_IH_comb, WMMd_inhibitor_comb)

    # Save the data
    save_dataframe(df_total_switch_GF,'df_cell_frac_IH_switch_GF_IH_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_WMMd, 'df_cell_frac_IH_switch_WMMd_IH_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_comb, 'df_cell_frac_IH_switch_comb_IH_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_GF, 'df_cell_frac_IH_continuous_GF_IH_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_WMMd, 'df_cell_frac_IH_continuous_WMMd_IH_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_comb, 'df_cell_frac_IH_continuous_comb_IH_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(2, 3, figsize=(20, 9))

    # Plot the data without drug holidays in the first plot
    df_total_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction', fontsize=11)
    axs[0, 0].set_title(f"Traditional therapy MMd GF IH ")
    axs[0, 0].grid(True)

    # Plot the data without drug holidays in the second plot
    df_total_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel(' ')
    axs[0, 1].set_title(r"Traditional therapy $W_{MMd}$ IH")
    axs[0, 1].grid(True)

    # Plot the data without drug holidays in the third plot
    df_total_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 2])
    axs[0, 2].set_xlabel(' ')
    axs[0, 2].set_ylabel(' ')
    axs[0, 2].set_title(r"Traditional therapy MMd GF IH and $W_{MMd}$ IH")
    axs[0, 2].grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations', fontsize=11)
    axs[1, 0].set_ylabel('Fraction', fontsize=11)
    axs[1, 0].set_title(f"Adaptive therapy MMd GF IH")
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fifth plot
    df_total_switch_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations', fontsize=11)
    axs[1, 1].set_ylabel(' ')
    axs[1, 1].set_title(r"Adaptive therapy $W_{MMd}$ IH")
    axs[1, 1].grid(True)

    # Plot the data with drug holidays in the sixth plot
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 2])
    axs[1, 2].set_xlabel('Generations', fontsize=11)
    axs[1, 2].set_ylabel(' ')
    axs[1, 2].set_title(r"Adaptive therapy MMd GF IH and $W_{MMd}$ IH")
    axs[1, 2].grid(True)

    # Create a single legend outside of all plots
    legend_labels = ['Fraction OC', 'Fraction OB', 'Fraction MMd', 'Fraction MMr']
    fig.legend(labels = legend_labels, loc='upper center', ncol=4, fontsize='large')
    save_Figure(plt, 'line_plot_cell_frac_IH_AT_MTD_a_h',
                                 r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

""" Figure to determine the difference between traditional and adaptive therapy
Shorter holiday and administration periods and weaker IHs compared to the original
situation"""
def Figure_continuous_MTD_vs_AT_realistic(n_switches, t_steps_drug):
    """ Function that makes a figure with 6 subplots showing the cell type
    fraction dynamics by traditional therapy (continuous MTD) and adaptive
    therapy.The holiday and administration periods are short (5 generations) and
    the IHs are weaker. It also prints the fraction values in the new equilibrium
    during adaptive and traditional therapy.

    Parameters:
    -----------
    n_switches: Int
        The fraction of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the fraction of time steps drugs are administared and the
        breaks are for the different Figures.
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.4, 2.2, 1.5],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.4]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.4, 2.2, 1.5],
        [0.95, 0.0, -0.5, -0.5],
        [0.55, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.4]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.4, 2.2, 1.5],
        [0.95, 0.0, -0.5, -0.5],
        [1.28, 0.0, 0.2, 0.0],
        [1.9, 0.0, -1.1, 0.4]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.65

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.35

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF = switch_dataframe(10, n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMd = switch_dataframe(10, n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb = switch_dataframe(10, n_switches, t_steps_drug[2],
                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_IH_comb,
                WMMd_inhibitor_comb)

    # Make dataframes for continiously administration
    df_total_GF = continuous_add_IH_df(10, 100, xOC, xOB, xMMd, xMMr, N, cOC,
            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_WMMd = continuous_add_IH_df(10, 100, xOC, xOB, xMMd, xMMr, N, cOC,
                            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                            matrix_no_GF_IH, WMMd_inhibitor)
    df_total_comb = continuous_add_IH_df(10, 100, xOC, xOB, xMMd, xMMr, N, cOC,
                            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                            matrix_IH_comb, WMMd_inhibitor_comb)

    # Print the equilibrium MMd and MMr values caused by the adaptive therapy
    # Print the equilibrium MMd and MMr values caused by the adaptive therapy
    avarage_MMr_MMd_nr(df_total_switch_GF, 10, 'Adaptive thearpy MMd GF IH')
    avarage_MMr_MMd_nr(df_total_switch_WMMd, 10, 'Adaptive thearpy WMMd IH')
    avarage_MMr_MMd_nr(df_total_switch_comb, 10, 'Adaptive thearpy IH combination')
    avarage_MMr_MMd_nr(df_total_GF, 10, 'Traditional thearpy MMd GF IH')
    avarage_MMr_MMd_nr(df_total_WMMd, 10, 'Traditional thearpy WMMd IH')
    avarage_MMr_MMd_nr(df_total_comb, 10, 'Traditional thearpy IH combination')

    # Save the data
    save_dataframe(df_total_switch_GF,'df_cell_frac_IH_switch_GF_IH_r.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_WMMd,'df_cell_frac_IH_switch_WMMd_IH_r.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_comb,'df_cell_frac_IH_switch_comb_IH_r.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_GF, 'df_cell_frac_IH_continuous_GF_IH_r.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_WMMd,'df_cell_frac_IH_continuous_WMMd_IH_r.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_comb,'df_cell_frac_IH_continuous_comb_IH_r.csv',
                                        r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(2, 3, figsize=(20, 9))

    # Plot the data without drug holidays in the first plot
    df_total_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[0, 0])
    axs[0, 0].axvspan(xmin=10, xmax=102, color='lightgray', alpha=0.45)
    axs[0, 0].set_xlim(1, 102)
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel(r'Cell fraction ($x_{i}$)', fontsize=13)
    axs[0, 0].set_title(f"Traditional therapy MMd GF IH ", fontsize=14)
    axs[0, 0].grid(True, linestyle='--')

    # Plot the data without drug holidays in the second plot
    df_total_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                legend=False, ax=axs[0, 1])
    axs[0, 1].axvspan(xmin=10, xmax=102, color='lightgray', alpha=0.45)
    axs[0, 1].set_xlim(1, 102)
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel(' ')
    axs[0, 1].set_title(r"Traditional therapy $W_{MMd}$ IH", fontsize=14)
    axs[0, 1].grid(True, linestyle='--')

    # Plot the data without drug holidays in the third plot
    df_total_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[0, 2])
    axs[0, 2].axvspan(xmin=10, xmax=102, color='lightgray', alpha=0.45)
    axs[0, 2].set_xlim(1, 102)
    axs[0, 2].set_xlabel(' ')
    axs[0, 2].set_ylabel(' ')
    axs[0, 2].set_title(r"Traditional therapy IH combination", fontsize=14)
    axs[0, 2].grid(True, linestyle='--')

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[1, 0])
    axs[1, 0].axvspan(xmin=10, xmax=102, color='lightgray', alpha=0.45)
    axs[1, 0].set_xlim(1, 102)
    axs[1, 0].set_xlabel('Generations', fontsize=13)
    axs[1, 0].set_ylabel(r'Cell fraction ($x_{i}$)', fontsize=13)
    axs[1, 0].set_title(f"Adaptive therapy MMd GF IH", fontsize=14)
    axs[1, 0].grid(True, linestyle='--')

    # Plot the data with drug holidays in the fifth plot
    df_total_switch_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[1, 1])
    axs[1, 1].axvspan(xmin=10, xmax=102, color='lightgray', alpha=0.45)
    axs[1, 1].set_xlim(1, 102)
    axs[1, 1].set_xlabel('Generations', fontsize=13)
    axs[1, 1].set_ylabel(' ')
    axs[1, 1].set_title(r"Adaptive therapy $W_{MMd}$ IH", fontsize=14)
    axs[1, 1].grid(True, linestyle='--')

    # Plot the data with drug holidays in the sixth plot
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[1, 2])
    axs[1, 2].axvspan(xmin=10, xmax=102, color='lightgray', alpha=0.45)
    axs[1, 2].set_xlim(1, 102)
    axs[1, 2].set_xlabel('Generations', fontsize=13)
    axs[1, 2].set_ylabel(' ')
    axs[1, 2].set_title(r"Adaptive therapy IH combination", fontsize=14)
    axs[1, 2].grid(True, linestyle='--')

    # Create a single legend outside of all plots
    legend_labels = ['OC fraction', 'OB fraction', 'MMd fraction',
                                                    'MMr fraction', 'Therapy']
    fig.legend(labels = legend_labels, loc='upper center', ncol=5,
                                                            fontsize='x-large')
    save_Figure(plt, 'line_plot_cell_frac_IH_AT_MTD_r',
                                 r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

""" Figure to determine the difference between traditional and adaptive therapy
The AT administration and holiday durations depend on the MMd and MMr fraction"""
def Figure_AT_MMd_MMr_limit(upper_limit_MMd, upper_limit_MMr):
    """ Function that makes a figure with 3 subplots showing the cell fraction
    dynamics during adaptive therapy. The IH administration starts when MMd
    because too high and stops when the MMr becomes too high. It prints the
    average adinistration and holiday duration

    Parameters:
    -----------
    upper_limit_MMd: Int
        The maximum fraction of MMd, when reached the IH administration starts
    upper_limit_MMr: Int
        The maximum fraction of MMr, when reached the IH administration stops
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.4, 2.0, 1.5],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.4]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.4, 2.0, 1.5],
        [0.95, 0.0, -0.5, -0.5],
        [0.55, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.4]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.4, 2.0, 1.5],
        [0.95, 0.0, -0.5, -0.5],
        [1.28, 0.0, 0.2, 0.0],
        [1.9, 0.0, -1.1, 0.4]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.65

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.35

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF, a_dur_GF, h_dur_GF = dynamics_MMd_MMr_limits(15, 150,
                upper_limit_MMd, upper_limit_MMr, xOC, xOB, xMMd, xMMr, N, cOC,
                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMd, a_dur_W, h_dur_W = dynamics_MMd_MMr_limits(15, 150,
       upper_limit_MMd, upper_limit_MMr, xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
       cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb, a_dur_comb, h_dur_comb = dynamics_MMd_MMr_limits(15,
                150, upper_limit_MMd, upper_limit_MMr, xOC, xOB, xMMd, xMMr,
                N, cOC, cOB, cMMd,  cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                matrix_IH_comb, WMMd_inhibitor_comb)

    # Print average holiday and administration duration
    print(f"""The average MMd GF IH administration duration is
    {round(a_dur_GF, 0)} generations and the average MMd GF IH holiday duration
    is {round(h_dur_GF, 0)} generations""")
    print(f"""The average WMMd IH administration duration is {round(a_dur_W, 0)}
    generations and the average WMMd IH holiday duration is {round(h_dur_W, 0)}
    generations""")
    print(f"""The average IH combination administration duration is
    {round(a_dur_comb, 0)} generations and the average IH combination holiday
    duration is {round(h_dur_comb, 0)} generations""")

    # Save the data
    save_dataframe(df_total_switch_GF,'df_cell_frac_IH_switch_GF_IH_d.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_WMMd,'df_cell_frac_IH_switch_WMMd_IH_d.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_comb,'df_cell_frac_IH_switch_comb_IH_d.csv',
                                        r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(1, 3, figsize=(20, 5))

    # Plot the data of the AT based on the MMd and MMr number (MMd GF IH)
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[0])
    axs[0].axvspan(xmin=15, xmax=152, color='lightgray', alpha=0.45)
    axs[0].set_xlim(1, 152)
    axs[0].set_xlabel('Generations', fontsize=12)
    axs[0].set_ylabel(r'Cell fraction ($x_{i}$)', fontsize=12)
    axs[0].set_title(f"Adaptive therapy MMd GF IH ", fontsize=14)
    axs[0].grid(True, linestyle='--')

    # Plot the data of the AT based on the MMd and MMr number (WMMd IH)
    df_total_switch_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                legend=False, ax=axs[1])
    axs[1].axvspan(xmin=15, xmax=152, color='lightgray', alpha=0.45)
    axs[1].set_xlim(1, 152)
    axs[1].set_xlabel('Generations', fontsize=12)
    axs[1].set_ylabel(' ')
    axs[1].set_title(r"Adaptive therapy $W_{MMd}$ IH", fontsize=14)
    axs[1].grid(True, linestyle='--')

    # Plot the data of the AT based on the MMd and MMr number (IH combination)
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                    color= ['tab:pink', 'tab:purple', 'tab:blue', 'tab:red'],
                                                    legend=False, ax=axs[2])
    axs[2].axvspan(xmin=15, xmax=152, color='lightgray', alpha=0.45)
    axs[2].set_xlim(1, 152)
    axs[2].set_xlabel('Generations', fontsize=12)
    axs[2].set_ylabel(' ')
    axs[2].set_title(r"Adaptive therapy IH combination", fontsize=14)
    axs[2].grid(True, linestyle='--')

    # Create a single legend outside of all plots
    legend_labels = ['OC fraction', 'OB fraction', 'MMd fraction',
                                                    'MMr fraction', 'Therapy']
    fig.legend(labels = legend_labels, loc='upper center', ncol=5,
                                                            fontsize='x-large')
    save_Figure(plt, 'line_plot_cell_frac_IH_AT_MTD_d',
                                 r'..\visualisation\results_model_frac_IH_inf')
    plt.show()


""" Figure to determine the difference between traditional and adaptive therapy.
Shorter holiday and administration periods compared to the original situation"""
def Figure_continuous_MTD_vs_AT_short_a_h(n_switches, t_steps_drug):
    """ Function that makes a figure with 6 subplots showing the cell type
    fraction dynamics by traditional therapy (continuous MTD) and adaptive
    therapy. The holiday and administration periods are short (5 generations).

    Parameters:
    -----------
    n_switches: Int
        The fraction of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the fraction of time steps drugs are administared and the
        breaks are for the different Figures.
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [0.5, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [1.2, 0, 0.2, 0.0],
        [1.9, 0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.6

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.45

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF = switch_dataframe(15, n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMd = switch_dataframe(15, n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb = switch_dataframe(15, n_switches, t_steps_drug[2],
                                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_IH_comb, WMMd_inhibitor_comb)

    # Make dataframes for continiously administration
    df_total_GF = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_WMMd = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_no_GF_IH, WMMd_inhibitor)
    df_total_comb = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_IH_comb, WMMd_inhibitor_comb)

    # Save the data
    save_dataframe(df_total_switch_GF, 'df_cell_frac_IH_switch_GF_IH_short_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_WMMd, 'df_cell_frac_IH_switch_WMMd_IH_short_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_comb, 'df_cell_frac_IH_switch_comb_IH_short_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_GF, 'df_cell_frac_IH_continuous_GF_IH_short_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_WMMd, 'df_cell_frac_IH_continuous_WMMd_IH_short_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_comb, 'df_cell_frac_IH_continuous_comb_IH_short_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(2, 3, figsize=(20, 9))

    # Plot the data without drug holidays in the first plot
    df_total_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction', fontsize=11)
    axs[0, 0].set_title(f"Traditional therapy MMd GF IH ")
    axs[0, 0].grid(True)

    # Plot the data without drug holidays in the second plot
    df_total_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel(' ')
    axs[0, 1].set_title(r"Traditional therapy $W_{MMd}$ IH")
    axs[0, 1].grid(True)

    # Plot the data without drug holidays in the third plot
    df_total_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 2])
    axs[0, 2].set_xlabel(' ')
    axs[0, 2].set_ylabel(' ')
    axs[0, 2].set_title(r"Traditional therapy MMd GF IH and $W_{MMd}$ IH")
    axs[0, 2].grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations', fontsize=11)
    axs[1, 0].set_ylabel('Fraction', fontsize=11)
    axs[1, 0].set_title(f"Adaptive therapy MMd GF IH")
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fifth plot
    df_total_switch_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations', fontsize=11)
    axs[1, 1].set_ylabel(' ')
    axs[1, 1].set_title(r"Adaptive therapy $W_{MMd}$ IH")
    axs[1, 1].grid(True)

    # Plot the data with drug holidays in the sixth plot
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 2])
    axs[1, 2].set_xlabel('Generations', fontsize=11)
    axs[1, 2].set_ylabel(' ')
    axs[1, 2].set_title(r"Adaptive therapy MMd GF IH and $W_{MMd}$ IH")
    axs[1, 2].grid(True)

    # Create a single legend outside of all plots
    legend_labels = ['Fraction OC', 'Fraction OB', 'Fraction MMd', 'Fraction MMr']
    fig.legend(labels = legend_labels, loc='upper center', ncol=4,
                                                                fontsize='large')
    save_Figure(plt, 'line_plot_cell_frac_IH_AT_MTD_short_a_h',
                             r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

""" Figure to determine the difference between traditional and adaptive therapy
Weaker IHs compared to the original situation"""
def Figure_continuous_MTD_vs_AT_weak_a_h(n_switches, t_steps_drug):
    """ Function that makes a figure with 6 subplots showing the cell type
    fraction dynamics by traditional therapy (continuous MTD) and adaptive
    therapy. The IHs are realively weak.

    Parameters:
    -----------
    n_switches: Int
        The fraction of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the fraction of time steps drugs are administared and the
        breaks are for the different Figures.
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [0.73, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [1.22, 0, 0.2, 0.0],
        [1.9, 0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.55

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.2

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF = switch_dataframe(15, n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMd = switch_dataframe(15, n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb = switch_dataframe(15, n_switches, t_steps_drug[2],
                                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_IH_comb, WMMd_inhibitor_comb)

    # Make dataframes for continiously administration
    df_total_GF = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_WMMd = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_no_GF_IH, WMMd_inhibitor)
    df_total_comb = continuous_add_IH_df(15, 135, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_IH_comb, WMMd_inhibitor_comb)

    # Save the data
    save_dataframe(df_total_switch_GF, 'df_cell_frac_IH_switch_GF_IH_weak_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_WMMd, 'df_cell_frac_IH_switch_WMMd_IH_weak_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_comb, 'df_cell_frac_IH_switch_comb_IH_weak_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_GF, 'df_cell_frac_IH_continuous_GF_IH_weak_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_WMMd, 'df_cell_frac_IH_continuous_WMMd_IH_weak_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_comb, 'df_cell_frac_IH_continuous_comb_IH_weak_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(2, 3, figsize=(20, 9))

    # Plot the data without drug holidays in the first plot
    df_total_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction', fontsize=11)
    axs[0, 0].set_title(f"Traditional therapy MMd GF IH ")
    axs[0, 0].grid(True)

    # Plot the data without drug holidays in the second plot
    df_total_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel(' ')
    axs[0, 1].set_title(r"Traditional therapy $W_{MMd}$ IH")
    axs[0, 1].grid(True)

    # Plot the data without drug holidays in the third plot
    df_total_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 2])
    axs[0, 2].set_xlabel(' ')
    axs[0, 2].set_ylabel(' ')
    axs[0, 2].set_title(r"Traditional therapy MMd GF IH and $W_{MMd}$ IH")
    axs[0, 2].grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations', fontsize=11)
    axs[1, 0].set_ylabel('Fraction', fontsize=11)
    axs[1, 0].set_title(f"Adaptive therapy MMd GF IH")
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fifth plot
    df_total_switch_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations', fontsize=11)
    axs[1, 1].set_ylabel(' ')
    axs[1, 1].set_title(r"Adaptive therapy $W_{MMd}$ IH")
    axs[1, 1].grid(True)

    # Plot the data with drug holidays in the sixth plot
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 2])
    axs[1, 2].set_xlabel('Generations', fontsize=11)
    axs[1, 2].set_ylabel(' ')
    axs[1, 2].set_title(r"Adaptive therapy MMd GF IH and $W_{MMd}$ IH")
    axs[1, 2].grid(True)

    # Create a single legend outside of all plots
    legend_labels = ['Fraction OC', 'Fraction OB', 'Fraction MMd', 'Fraction MMr']
    fig.legend(labels = legend_labels, loc='upper center', ncol=4,
                                                               fontsize='large')
    save_Figure(plt, 'line_plot_cell_frac_IH_AT_MTD_weak_a_h',
                             r'..\visualisation\results_model_frac_IH_inf')
    plt.show()


""" Figure to determine the difference between traditional and adaptive therapy
whereby the OB-OC equilibrium get restored"""
def Figure_continuous_MTD_vs_AT_OB_a_h(n_switches, t_steps_drug):
    """ Function that makes a figure with 6 subplots showing the cell type
    fraction dynamics by traditional therapy (continuous MTD) and adaptive therapy
    whereby the OB-OC equilibrium get restored.

    Parameters:
    -----------
    n_switches: Int
        The fraction of switches between giving drugs and not giving drugs.
    t_steps_drug: List
        List with the fraction of time steps drugs are administared and the
        breaks are for the different Figures.
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

    cOC_IH = 1.1
    cOB_IH = 0.64

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [0.5, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [1.2, 0.0, 0.2, 0.0],
        [1.9, 0.0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.6

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.45

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_GF = switch_dataframe(15, n_switches, t_steps_drug[0],
                t_steps_drug[0], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_switch_WMMd = switch_dataframe(15, n_switches, t_steps_drug[1],
                t_steps_drug[1], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)
    df_total_switch_comb = switch_dataframe(15, n_switches, t_steps_drug[2],
                t_steps_drug[2], xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd, cMMr,
                cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_IH_comb,
                WMMd_inhibitor_comb)

    # Make dataframes for continiously administration
    df_total_GF = continuous_add_IH_df(15, 110, xOC, xOB, xMMd, xMMr, N, cOC,
            cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)
    df_total_WMMd = continuous_add_IH_df(15, 110, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_no_GF_IH, WMMd_inhibitor)
    df_total_comb = continuous_add_IH_df(15, 110, xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_IH_comb, WMMd_inhibitor_comb)


    # Save the data
    save_dataframe(df_total_switch_GF,'df_cell_frac_IH_switch_GF_IH_OB_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_WMMd, 'df_cell_frac_IH_switch_WMMd_IH_OB_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_comb, 'df_cell_frac_IH_switch_comb_IH_OB_a_h.csv',
                                        r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_GF, 'df_cell_frac_IH_continuous_GF_IH_OB_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_WMMd, 'df_cell_frac_IH_continuous_WMMd_IH_OB_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_comb, 'df_cell_frac_IH_continuous_comb_IH_OB_a_h.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(2, 3, figsize=(20, 9))

    # Plot the data without drug holidays in the first plot
    df_total_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction', fontsize=11)
    axs[0, 0].set_title(f"Traditional therapy MMd GF IH ")
    axs[0, 0].grid(True)

    # Plot the data without drug holidays in the second plot
    df_total_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel(' ')
    axs[0, 1].set_title(r"Traditional therapy $W_{MMd}$ IH")
    axs[0, 1].grid(True)

    # Plot the data without drug holidays in the third plot
    df_total_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[0, 2])
    axs[0, 2].set_xlabel(' ')
    axs[0, 2].set_ylabel(' ')
    axs[0, 2].set_title(r"Traditional therapy MMd GF IH and $W_{MMd}$ IH")
    axs[0, 2].grid(True)

    # Plot the data with drug holidays in the fourth plot
    df_total_switch_GF.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 0])
    axs[1, 0].set_xlabel('Generations', fontsize=11)
    axs[1, 0].set_ylabel('Fraction', fontsize=11)
    axs[1, 0].set_title(f"Adaptive therapy MMd GF IH")
    axs[1, 0].grid(True)
    plt.grid(True)

    # Plot the data with drug holidays in the fifth plot
    df_total_switch_WMMd.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 1])
    axs[1, 1].set_xlabel('Generations', fontsize=11)
    axs[1, 1].set_ylabel(' ')
    axs[1, 1].set_title(r"Adaptive therapy $W_{MMd}$ IH")
    axs[1, 1].grid(True)

    # Plot the data with drug holidays in the sixth plot
    df_total_switch_comb.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                                                    legend=False, ax=axs[1, 2])
    axs[1, 2].set_xlabel('Generations', fontsize=11)
    axs[1, 2].set_ylabel(' ')
    axs[1, 2].set_title(r"Adaptive therapy MMd GF IH and $W_{MMd}$ IH")
    axs[1, 2].grid(True)

    # Create a single legend outside of all plots
    legend_labels = ['Fraction OC', 'Fraction OB', 'Fraction MMd', 'Fraction MMr']
    fig.legend(labels = legend_labels, loc='upper center', ncol=4,
                                                                fontsize='large')
    save_Figure(plt, 'line_plot_cell_frac_IH_AT_MTD_OB_a_h',
                             r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

""" 3D plot showing the best IH holiday and administration periods"""
def Figure_3D_MM_frac_IH_add_and_holiday():
    """ Figure that makes three 3D plot that shows the average MM fraction for
    different holiday and administration periods of only MMd GF inhibitor, only
    WMMd inhibitor or both. It prints the IH administration periods and holidays
    that caused the lowest total MM fraction."""

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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.4, 2.2, 1.6],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.4]])

    # Payoff matrix when only GF inhibitor drugs are present
    matrix_GF_IH = np.array([
        [0.0, 1.4, 2.2, 1.6],
        [0.95, 0.0, -0.5, -0.5],
        [0.73, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.4]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_IH_comb = np.array([
        [0.0, 1.4, 2.2, 1.6],
        [0.95, 0.0, -0.5, -0.5],
        [1.1, 0, 0.2, 0.0],
        [1.9, 0, -1.1, 0.4]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_comb = 0.7

    # WMMd inhibitor effect when only WMMd IH is present
    WMMd_inhibitor = 1.21

    # Create a dataframe
    df_holiday_GF_IH = dataframe_3D_plot( xOC, xOB, xMMd, xMMr, N, cOC, cOB,
        cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH)

    # Save the data
    save_dataframe(df_holiday_GF_IH, 'df_cell_frac_IH_best_MMd_GF_IH_holiday.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Determine the axis values
    X_GF_IH, Y_GF_IH, Z_GF_IH = x_y_z_axis_values_3d_plot(df_holiday_GF_IH,
                                                                        'GF IH')

    # Create a dataframe
    df_holiday_W_IH = dataframe_3D_plot(xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
        cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_no_GF_IH, WMMd_inhibitor)

    # Save the data
    save_dataframe(df_holiday_W_IH, 'df_cell_frac_IH_best_WMMd_IH_holiday.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Determine the axis values
    X_W_IH, Y_W_IH, Z_W_IH = x_y_z_axis_values_3d_plot(df_holiday_W_IH, "W IH")

    # Create a dataframe
    df_holiday_comb = dataframe_3D_plot(xOC, xOB, xMMd, xMMr, N, cOC,
                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_IH_comb,
                WMMd_inhibitor_comb)

    # Save the data
    save_dataframe(df_holiday_comb, 'df_cell_frac_IH_best_comb_IH_holiday.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Determine the axis values
    X_comb, Y_comb, Z_comb = x_y_z_axis_values_3d_plot(df_holiday_comb,
                                                            'IH combination')

    # Create a figure and a grid of subplots
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), subplot_kw={'projection': \
                        '3d'}, gridspec_kw={'hspace': 0.25, 'wspace': 0.25})

    # Plot each subplot
    for i, ax in enumerate(axes.flat, start=1):
        if i == 1:
            surf = ax.plot_surface(X_W_IH, Y_W_IH, Z_W_IH, cmap='coolwarm')

            # Add labels
            ax.set_ylabel('Generations admin')
            ax.set_xlabel('Generations holiday')
            ax.set_zlabel('MM fraction')
            ax.set_title(r'A) $W_{MMd}$ IH', pad=10)

            # Turn to the right angle
            ax.view_init(elev = 32, azim = -140)

            # Add a color bar
            color_bar = fig.colorbar(surf, ax=ax, shrink=0.4, location= 'right')
            color_bar.set_label('MM fraction')

        elif i == 2:
            surf = ax.plot_surface(X_GF_IH, Y_GF_IH, Z_GF_IH, cmap = 'coolwarm')

            # Add labels
            ax.set_ylabel('Generations admin')
            ax.set_xlabel('Generations holiday')
            ax.set_zlabel('MM fraction')
            ax.set_title('B)  MMd GF IH', pad=10)

            # Turn to the right angle
            ax.view_init(elev = 38, azim = -133)

            # Add a color bar
            color_bar = fig.colorbar(surf, ax=ax, shrink=0.4, location= 'right')

            color_bar.set_label('MM fraction')

        elif i == 3:
            surf = ax.plot_surface(X_comb, Y_comb, Z_comb, cmap = 'coolwarm')

            # Add labels
            ax.set_ylabel('Generations admin')
            ax.set_xlabel('Generations holiday')
            ax.set_zlabel('MM fraction')
            ax.set_title('C)  IH combination', pad=10)

            # Turn to the right angle
            ax.view_init(elev = 43, azim = -148)

            # Add a color bar
            color_bar = fig.colorbar(surf, ax=ax, shrink=0.4, location= 'right')
            color_bar.set_label('MM fraction')

        else:
            # Hide the emply subplot
            ax.axis('off')

    # Add a color bar
    save_Figure(fig, '3d_plot_MM_frac_IH_best_IH_h_a_periods',
                                r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

""" 3D plot showing the best IH strengths """
def Figure_3D_MM_frac_MMd_IH_strength():
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are pressent
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.77, 0.2]])

    # Payoff matrix when GF inhibitor drugs are pressent
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [1.5, 0, 0.2, 0.0],
        [1.9, 0, -0.77, 0.2]])

    # administration and holiday periods
    t_steps_drug = 8
    t_steps_no_drug = 8

    # Make a dataframe
    column_names = ['Strength WMMd IH', 'Strength MMd GF IH', 'MM fraction']
    df_holiday = pd.DataFrame(columns=column_names)

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

            frac_tumour = minimal_tumour_frac_t_steps(t_steps_drug,
                        t_steps_no_drug, xOC, xOB, xMMd, xMMr, N, cOC, cOB, cMMd,
                        cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH, matrix_GF_IH,
                        WMMd_inhibitor)

            # Add results to the dataframe
            new_row_df = pd.DataFrame([{'Strength WMMd IH':\
                        round(strength_WMMd_IH/ 10, 1), 'Strength MMd GF IH': \
                round(strength_MMd_GF_IH/ 10, 1), 'MM fraction': frac_tumour}])

            df_holiday = combine_dataframes(df_holiday, new_row_df)

    # Save the data
    save_dataframe(df_holiday, 'df_cell_frac_IH_best_comb_IH_strength.csv',
                                         r'..\data\data_model_frac_IH_inf')


    # Find the drug administration and holiday period causing the lowest MM
    # fraction
    min_index = df_holiday['MM fraction'].idxmin()
    strength_WMMd_min = df_holiday.loc[min_index, 'Strength WMMd IH']
    strength_MMd_GF_min = df_holiday.loc[min_index, 'Strength MMd GF IH']
    frac_min = df_holiday.loc[min_index, 'MM fraction']

    print(f"""Lowest MM fraction: {frac_min}-> MMd GF IH strength is
        {strength_MMd_GF_min} and WMMd IH strength is {strength_WMMd_min}""")

    # Avoid errors because of the wrong datatype
    df_holiday['Strength WMMd IH'] = pd.to_numeric(df_holiday[\
                                        'Strength WMMd IH'], errors='coerce')
    df_holiday['Strength MMd GF IH'] = pd.to_numeric(df_holiday[\
                                        'Strength MMd GF IH'], errors='coerce')
    df_holiday['MM fraction'] = pd.to_numeric(df_holiday['MM fraction'],
                                                                errors='coerce')

    # Make a meshgrid for the plot
    X = df_holiday['Strength WMMd IH'].unique()
    Y = df_holiday['Strength MMd GF IH'].unique()
    X, Y = np.meshgrid(X, Y)
    Z = np.zeros((21, 21))

    # Fill the 2D array with the MM fraction values by looping over each row
    for index, row in df_holiday.iterrows():
        i = int(row.iloc[0]*10)
        j = int(row.iloc[1]*10)
        Z[j, i] = row.iloc[2]

    # Make a 3D Figure
    fig = plt.figure(figsize = (8, 6))
    ax = fig.add_subplot(111, projection = '3d')
    surf = ax.plot_surface(X, Y, Z, cmap = 'coolwarm')

    # Add labels
    ax.set_xlabel(r'Strength $W_{MMd}$ IH')
    ax.set_ylabel('Strength MMd GF IH')
    ax.set_zlabel('MM fraction')
    ax.set_title(r"""Average MM fraction with varying $W_{MMd}$ IH and
    MMd GF IH strengths""")

    # Turn to the right angle
    ax.view_init(elev = 40, azim = -70)

    # Add a color bar
    color_bar = fig.colorbar(surf, shrink = 0.6, location= 'left')
    color_bar.set_label('MM fraction')

    save_Figure(fig, '3d_plot_MM_frac_IH_best_IH_strength',
                                r'..\visualisation\results_model_frac_IH_inf')
    plt.show()


""" Figure with a longer IH administration than holiday and the other way around"""
def Figure_duration_A_h_MMd_IH(n_switches, t_steps_drug, t_steps_no_drug):
    """ Function that makes a Figure with two subplots one of the dynamics by a
    longer IH administration than holiday and one of the dynamics by a longer IH
    than administration.

    Parameters:
    -----------
    n_switches: List
        List with the fraction of switches between giving drugs and not giving
        drugs.
    t_steps_drug: List
        List with the fraction of time steps drugs are administared.
    t_steps_no_drug: List
        List with the fraction of time steps drugs are not administared (holiday).
    """
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix when no drugs are present
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0, 0.2, 0.0],
        [1.9, 0, -0.8, 0.2]])

    # Payoff matrix when both inhibitor drugs are present
    matrix_GF_IH_half = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [1.15, 0, 0.2, 0.0],
        [1.9, 0, -1.1, 0.2]])

    # WMMd inhibitor effect when both inhibitor drugs are present
    WMMd_inhibitor_half = 0.6

    # Make dataframe for the different drug hollyday duration values
    df_total_switch_1 = switch_dataframe(15, n_switches[0], t_steps_drug[0],
                                t_steps_no_drug[0], xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_GF_IH_half, WMMd_inhibitor_half)
    df_total_switch_2 = switch_dataframe(15, n_switches[1], t_steps_drug[1],
                                t_steps_no_drug[1], xOC, xOB, xMMd, xMMr, N, cOC,
                                cOB, cMMd, cMMr, cOC_IH, cOB_IH, matrix_no_GF_IH,
                                matrix_GF_IH_half, WMMd_inhibitor_half)

    # Save the data
    save_dataframe(df_total_switch_1, 'df_cell_frac_IH_short_a_long_h_MMd_IH.csv',
                                         r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_total_switch_2, 'df_cell_frac_IH_long_a_short_h_MMd_IH.csv.csv',
                                         r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
    g = 'generations'
    ta = t_steps_drug
    th = t_steps_no_drug

    # Plot the data with short administrations in the first plot
    df_total_switch_1.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                            label=[ 'Fraction OC', 'Fraction OB', 'Fraction MMd',
                            'Fraction MMr'], ax=axs[0])
    axs[0].set_xlabel('Generations')
    axs[0].set_ylabel('MM fraction')
    axs[0].set_title(f"""Dynamics when the IH administrations lasted {ta[0]} {g}
    and the IH holidays lasted {th[0]} {g}""")
    axs[0].legend(loc = 'upper right')
    axs[0].grid(True)

    # Plot the data with long administrations in the second plot
    df_total_switch_2.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                        label=['Fraction OC', 'Fraction OB', 'Fraction MMd',
                        'Fraction MMr'], ax=axs[1])
    axs[1].set_xlabel('Generations')
    axs[1].set_ylabel('MM fraction')
    axs[1].set_title(f"""Dynamics when the IH administrations lasted {ta[1]} {g}
    and the IH holidays lasted {th[1]} {g}""")
    axs[1].legend(loc = 'upper right')
    axs[1].grid(True)
    plt.grid(True)
    save_Figure(plt, 'line_plot_cell_frac_IH_diff_h_and_a_MMd_IH',
                                 r'..\visualisation\results_model_frac_IH_inf')
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

    cOC_IH = 1.1
    cOB_IH = 0.7

    # Payoff matrix
    matrix_no_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [2.2, 0.0, 0.2, 0.0],
        [1.9, 0.0, -0.77, 0.2]])

    t = np.linspace(0, 25, 25)

    # Initial conditions
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC, cOB, cMMd, cMMr, matrix_no_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_1_MMd_GF_IH= pd.DataFrame({'Generation': t, 'xOC': y[:, 0], 'xOB': \
                                y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Determine the current fractions
    xOC = df_1_MMd_GF_IH['xOC'].iloc[-1]
    xOB = df_1_MMd_GF_IH['xOB'].iloc[-1]
    xMMd = df_1_MMd_GF_IH['xMMd'].iloc[-1]
    xMMr = df_1_MMd_GF_IH['xMMr'].iloc[-1]

    # Payoff matrix
    matrix_GF_IH = np.array([
        [0.0, 1.6, 2.2, 1.9],
        [0.95, 0.0, -0.5, -0.5],
        [0.4, 0, 0.2, 0],
        [1.9, 0, -0.77, 0.2]])

    # Initial conditions
    t = np.linspace(25, 100, 75)
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC_IH, cOB_IH, cMMd, cMMr, matrix_GF_IH)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2_MMd_GF_IH= pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Combine the dataframes
    df_MMd_GF_IH= combine_dataframes(df_1_MMd_GF_IH, df_2_MMd_GF_IH)

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
    df_1_WMMd_IH = pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Determine the current fractions
    xOC = df_1_WMMd_IH['xOC'].iloc[-1]
    xOB = df_1_WMMd_IH['xOB'].iloc[-1]
    xMMd = df_1_WMMd_IH['xMMd'].iloc[-1]
    xMMr = df_1_WMMd_IH['xMMr'].iloc[-1]

    # Initial conditions
    t = np.linspace(25, 100, 75)
    WMMd_inhibitor =  1.7
    y0 = [xOC, xOB, xMMd, xMMr]
    parameters = (N, cOC_IH, cOB_IH, cMMd, cMMr, matrix_no_GF_IH, WMMd_inhibitor)

    # Determine the ODE solutions
    y = odeint(model_dynamics, y0, t, args=parameters)
    df_2_WMMd_IH= pd.DataFrame({'Generation': t, 'xOC': y[:, 0],
                            'xOB': y[:, 1], 'xMMd': y[:, 2], 'xMMr': y[:, 3]})

    # Combine the dataframes
    df_WMMd_IH= combine_dataframes(df_1_WMMd_IH, df_2_WMMd_IH)

    # Make dataframes for the fitness values
    df_fitness_WMMd_IH_1 = frac_to_fitness_values(df_1_WMMd_IH, N, cOC, cOB,
                                                    cMMd, cMMr, matrix_no_GF_IH)
    df_fitness_WMMd_IH_2 = frac_to_fitness_values(df_2_WMMd_IH, N, cOC_IH,
                            cOB_IH, cMMd, cMMr, matrix_no_GF_IH, WMMd_inhibitor)
    df_fitness_WMMd_IH= combine_dataframes(df_fitness_WMMd_IH_1,
                                                        df_fitness_WMMd_IH_2)

    df_fitness_MMd_GF_IH_1 = frac_to_fitness_values(df_1_MMd_GF_IH, N, cOC, cOB,
                                                    cMMd, cMMr, matrix_no_GF_IH)
    df_fitness_MMd_GF_IH_2 = frac_to_fitness_values(df_2_MMd_GF_IH, N, cOC_IH,
                                            cOB_IH, cMMd, cMMr, matrix_GF_IH)
    df_fitness_MMd_GF_IH= combine_dataframes(df_fitness_MMd_GF_IH_1,
                                                        df_fitness_MMd_GF_IH_2)

    # Save the data
    save_dataframe(df_WMMd_IH, 'df_cell_frac_WMMd_inhibit.csv',
                                            r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_MMd_GF_IH, 'df_cell_frac_MMd_GF_inhibit.csv',
                                             r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_fitness_WMMd_IH, 'df_fitness_WMMd_inhibit.csv',
                                             r'..\data\data_model_frac_IH_inf')
    save_dataframe(df_fitness_MMd_GF_IH, 'df_fitness_MMd_GF_inhibit.csv',
                                            r'..\data\data_model_frac_IH_inf')

    # Create a Figure
    fig, axs = plt.subplots(2, 2, figsize=(16, 8))

    # Plot first subplot
    df_WMMd_IH.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                        label=['Fraction OC', 'Fraction OB', 'Fraction MMd',
                                 'Fraction MMr'], ax=axs[0, 0])
    axs[0, 0].set_xlabel(' ')
    axs[0, 0].set_ylabel('Fraction')
    axs[0, 0].set_title(r'Fraction dynamics when a $W_{MMd}$ IH is administered')
    axs[0, 0].legend(loc = 'upper right')
    axs[0, 0].grid(True)

    # Plot the second subplot
    df_fitness_WMMd_IH.plot(y=['WOC', 'WOB', 'WMMd', 'WMMr', 'W_average'],
                            label = ['Fitness OC', 'Fitness OB', 'Fitness MMd',
                              'Fitness MMr', 'Average fitness'],  ax=axs[1, 0])
    axs[1, 0].set_title(r'Fitness dynamics when a $W_{MMd}$ IH is administered')
    axs[1, 0].set_xlabel('Generations')
    axs[1, 0].set_ylabel('Fitness')
    axs[1, 0].legend(['Fitness OC', 'Fitness OB', 'Fitness MMd', 'Fitness MMr',
                                                        'Average fitness'])
    axs[1, 0].legend(loc = 'upper right')
    axs[1, 0].grid(True)

    # Plot the third subplot
    df_MMd_GF_IH.plot(x='Generation', y=['xOC', 'xOB', 'xMMd', 'xMMr'],
                        label=['Fraction OC', 'Fraction OB', 'Fraction MMd',
                                                'Fraction MMr'], ax=axs[0, 1])
    axs[0, 1].set_xlabel(' ')
    axs[0, 1].set_ylabel('Fraction')
    axs[0, 1].set_title('Fraction dynamics when a MMd GF IH is administered')
    axs[0, 1].legend(loc = 'upper right')
    axs[0, 1].grid(True)

    # Plot the fourth subplot
    df_fitness_MMd_GF_IH.plot(y=['WOC', 'WOB', 'WMMd', 'WMMr', 'W_average'],
                             label = ['Fitness OC', 'Fitness OB', 'Fitness MMd',
                             'Fitness MMr', 'Average fitness'],  ax=axs[1, 1])
    axs[1, 1].set_title('Fitness dynamics when a MMd GF IH is administered')
    axs[1, 1].set_xlabel('Generations')
    axs[1, 1].set_ylabel('Fitness')
    axs[1, 1].legend(loc = 'upper right')
    axs[1, 1].grid(True)
    plt.tight_layout()
    save_Figure(plt, 'line_plot_cell_frac_fitness_drugs',
                                r'..\visualisation\results_model_frac_IH_inf')
    plt.show()

if __name__ == "__main__":
    main()
