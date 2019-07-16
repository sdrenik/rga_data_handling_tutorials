"""
testing library features while figuring out what it actually does (and how)
From: https://gitlab.mpcdf.mpg.de/geos/RGA_data_handling/blob/public/testlib.py
"""

import numpy as np
import matplotlib.pyplot as pp
import random

import rga_data_handling.Class as Class
from rga_data_handling.RGA_class_plotter import plot_data, show_results
import rga_data_handling.fit_many_times as fmt

# No need to import - these modules are imported by Class:
#import rga_data_handling.RGA_fitting as RGA_fitting
#import rga_data_handling.molecules3 as molecules


# made up test data
columns = {"time_1u": np.linspace(0,100,100),
        1: np.array([random.random() for i in range(100)])*1e-6,
        2: np.array([random.random() for i in range(100)])*1e-7,
        4: np.array([random.random() for i in range(100)])*1e-8,
        }
tags = {"time_col": "time_1u", "title": "testdata"}

# Create an rga.Trace object

tr = Class.Trace(columns, tags)

# check if the object is filled with data

tr.filled

# see what are the data properties

tr.tag

# plot the data
plot_data(tr)
# please note that, unlike your code, this plotting uses the lin y scale

# plot only some of the singals, i.e. masses 1 and 3
plot_data(tr, [1, 3])

# plot the data and save the plot to file
plot_data(tr, save_name='plot_image.png')

# non-zero background before the pulse? (e.g. from -15 s to -5 s)
tr.subtract_background([-15, -5])

# no signal is expected at mass 23 AMU. Still, there is some evolution at this mass
# This indicates the offset of the instrument caused by pulse operation (mag field, pressure jumps, etc)

tr.correct_offset(23)

# or, if there more such zero signals:

tr.correct_offset([23, 37, 43]) # here, an average value from each signal is used for offset correction

# this is where real data would be welcome

# identify the molecules that make up the recorded spectra

# define the candidate molecules for the fit

# hydrogen-containing molecules first
# these are defined with their cracking pattern (loaded from file, or default version used (hard-coded))
# their partial pressures (in arb.u.), and the average H/(H+D) ratio

H_molecules = {}

H_molecules['water'] = ['w', 'water', 'rw'] # [<partial pressure>, <name of molecule in the cracking pattern library>, <H/(H+D) ratio>]
# 'w' and 'rw' can be substituted for any string (with letters only)
# 'water' is the name of the molecule in the library

# The isotope ratio can be un-restricted (fit will try any value from 0 to 1), or restricted, such as:
H_molecules['methane'] = ['m', 'methane', ['rm', 0.0, 0.1]]
# or fixed
H_molecules['ammonia'] = ['a', 'ammonia', 0.65]

# or, one can have two species with the same isotope ratio
H_molecules['ammonia'] = ['a', 'ammonia', 'rw']


# non-hydrogen containing molecules
# these are defined just with their cracking pattern and partial pressure
non_H_molecules = {}
non_H_molecules['nitrogen'] = ['n', 'N2'] # [<fitting parameter for partial pressure - can be any string>, <cracking pattern library name>]
non_H_molecules['oxygen'] = ['o', 'O2']

# disregarded masses

# do not consider mass 16 AMU in the fit

# e.g. at high N2 pressures, the signal at 14 AMU is dominated by N2. Because N2 is sufficienlty well identified by 28 AMU,
# looking at 14 AMU too just causes unnecessary error in the fit


disregard = [16, # never use mass 16 AMU in the calculation
[14, 28, 1e-7]] # do not use mass 14 AMU, when the signal at 28 AMU is higher than 1e-7

# deconvolute the data from start_time to stop_time, in steps of <step> datapoints
start_time = 0
stop_time = 15
step = 2

tr.deconvolute(H_molecules, non_H_molecules, disregard, start_time, stop_time, step)

show_results(tr)

# the results are nice but the plot is dominated by the high N2 pressure that was not the main goal of the fit, anyway
show_results(tr, ['water', 'methane', 'ammonia'])

# what is the effect of poorly defined cracking patterns?
# perform the fit many times, each time with perturbed cracking patterns, then look at the average value

perturb = 0.1 # 10 % error of the cracking pattern
times = 25 # how many times will the fit be done

to_join = [[], ''] # a relict from previous versions that I have not yet moved to a more appropriate place, sorry

traces = fmt.fit_many_times(tr, times, perturb, to_join, H_molecules, non_H_molecules, disregard, start_time, stop_time, step)

# make the average trace
average_trace = fmt.povpreci(traces)

# plot the results
fmt.errorbar_results(average_trace)
plt.show()


# Exporting the data

# the Trace object has a funcion ".export". If used without argument, it will export the data in files named by .tag['title']:
# simulated intensities at corresponding masses, partial pressures, isotope ratios, fitting parameters and cracking patterns

# Apart from that, the fitted data can be accessed in the attribute ".rescols"

# In the many_times_fit, average_trace contains nothing but the fitted results.
