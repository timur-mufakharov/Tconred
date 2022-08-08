# Tconred
Tconred is the software for visualised data reduction of the Tianma 65-m telescope continuum observations.
It is written in python language with the PyQt4 toolkit. It is tested in Ubuntu 14.04 LTS, Ubuntu 16.04 LTS, and Mac OS El Capitan.
CalibratorsPlots - program to analyse data collected using previous program Tconred. It helps to control the observations quality along with calculation of some parameters.

##
Usage of Tconred:

1) Launch from command line as a python program: python Tconred.py
The workspace contains field (on the left) to choose directory and file, then display its information, another field on the right side is to plot the Left and Right polarization data for scan.
At the bottom there are buttons to save results of the Gauss fit (also file will contain name of the source, elevation, offset, HPBW etc).
The resulting files of this program could be used further to plot different distributions and calculate average values of different parameters for sources of interest.

2) Choose the directory with your fits files - press the button "Load files".

3) Click with the left mouse button to the "file from the list" - it will be displayed on the right. 
At the same time scan will be automatically fitted with the Gaussian, baseline will be removed and parameters of the fit will be displayed on the plot and in the text boxes at the bottom left. 

4) Go through the files to inspect them and, at the end, save all the results by clicking "Save LP results" and "Save RP results" button under the plot.
No need to click Save after every scan. Otherwise, if results are not needed, one must clear temporary files before closing the program - "Clear tmp file button".
Note 1: program creates temporary files for each scan when user click on it, if results are saved at the end, those temporary files cleared automatically, but if results are not saved they will remain (in a folder with Tconred.py).
Note 2: we put two Save buttons (LP and RP) because one of the polarizations might systematically be in poor condition. For example in 2016-2017 only right polarization in C-band is good. 

5) Program can be launched from any directory and resulting files will be saved in that directory with the program.
The Tconred program should work in any Unix system if the following requirements are met: python libraries and packages (astropy, scipy, numpy, PyQt4 etc).

###
Description of the available tools in the CalibratorsPlots.py:

1) Plot the gain curve and calculate second order polynomial equation to describe it (A, B, C coefficients an d fitting residuals).

2) Plot the Half Power Beam Width (HPBW) distribution and calculate its average value.

3) Plot the offsets distribution 

4) Plot the system temperature against time (in MJD) or against elevation 

Note! it works with numpy version 1.11.2. Unfortunately when using later version of numpy, points in the graphics are disappear and it gives an error message. This error rises from the pyqtgraph package and already been asked by other user in stackoverflow: https://stackoverflow.com/questions/45345527/pyqtgraph-gives-typeerror-with-symbols-python-2-7-13

###
Requirements:
Python 2.7

import os 
from os.path import isfile, join
from fnmatch import fnmatch
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from scipy import optimize
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.table import Table, Column

