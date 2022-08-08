#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import os # to list files, directories
from os.path import isfile, join # to list files
from os import system
from fnmatch import fnmatch # to match .fits .txt .. extenctions
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
from numpy import sqrt, pi, exp, linspace
from scipy import optimize
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.table import Table, Column

class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.initUI()


    def initUI(self):

        ## Set grid layout
        grid = QGridLayout()
        self.setLayout(grid)
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        ## X, Y positions and x,y size of the window
        self.setGeometry(300, 300, 1200, 600)
        self.setWindowTitle('Tconred')
        self.move(300, 300)

        ''' Create Buttons'''
        button0 = QPushButton('About Tconred')
        button0.clicked.connect(self.Help)
        button1 = QPushButton('Load files')
        button1.clicked.connect(self.showDialog)
        button1.setShortcut('Ctrl+O')
        button2 = QPushButton('Clear tmp files')
        button2.clicked.connect(self.clearResult)
        button3 = QPushButton('Quit')
        button3.clicked.connect(self.close)
        button_RP = QPushButton('Save RP results')
        button_RP.clicked.connect(self.combineRPresult)
        button_LP = QPushButton('Save LP results')
        button_LP.clicked.connect(self.combineLPresult)

        lbl1 = QLabel('Source')
        lbl2 = QLabel('Frequency (GHz)')
        lbl_gain = QLabel('Gain curve: A*el^2 + B*el + C')
        lbl_A = QLabel('A')
        lbl_B = QLabel('B')
        lbl_C = QLabel('C')
        lbl_LP = QLabel('Left polarization')
        lbl_RP = QLabel('Right polarization')

        self.list = QListWidget(self)
        self.list.itemClicked.connect(self.clickedList)
        self.cb = QCheckBox('Apply gain correction', self)
        self.cb.stateChanged.connect(self.GainCoeff)

        self.textbox2 = QLineEdit() #source
        self.textbox3 = QLineEdit() #freq
        self.textbox4 = QLineEdit() #A
        self.textbox5 = QLineEdit() #B
        self.textbox6 = QLineEdit() #C

        self.pw_LP = pg.PlotWidget()
        self.pw_RP = pg.PlotWidget()

        ''' Locate widgets '''
        grid.addWidget(button0, 10, 0)
        grid.addWidget(button1, 1, 0)
        grid.addWidget(button2, 10, 7)
        grid.addWidget(button3, 10, 8)
        grid.addWidget(lbl_gain, 5, 0, 1, 2)
        grid.addWidget(lbl_A, 6, 0)
        grid.addWidget(lbl_B, 7, 0)
        grid.addWidget(lbl_C, 8, 0)
        grid.addWidget(button_LP, 9, 3, 1, 3)
        grid.addWidget(button_RP, 9, 6, 1, 3)
        grid.addWidget(lbl1, 2, 0)
        grid.addWidget(lbl2, 3, 0)
        grid.addWidget(self.list, 4, 0, 1, 2)  #.fits files list
        grid.addWidget(lbl_LP, 1, 5)
        grid.addWidget(lbl_RP, 1, 8)
        grid.addWidget(self.textbox2, 2, 1)
        grid.addWidget(self.textbox3, 3, 1)
        grid.addWidget(self.textbox4, 6, 1)
        grid.addWidget(self.textbox5, 7, 1)
        grid.addWidget(self.textbox6, 8, 1)
        grid.addWidget(self.cb, 9, 0)
        #
        grid.addWidget(self.pw_LP, 2, 3, 6, 3)
        grid.addWidget(self.pw_RP, 2, 6, 6, 3)

        self.show()



    def showDialog(self):
        """ 1) choose path to open
            2) add fits files to the ListWidget """
        global pathname
        pathname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        files = [f for f in os.listdir(pathname) if os.path.isfile(join(pathname, f))]

        ''' select only fits files (to display in a list widget) '''
        pattern = "*.fits"
        names = []
        for name in files:
            if fnmatch(name, pattern):
               names.append(name) # write fits file to the list

        ''' add items to the list widget'''
        self.list.clear()
        self.list.addItems(names)


    def showRes(self):
        """ show calculated results from txt files """

        f = os.path.join(pathname, 'result_lp.txt')
        file = open(f,'r').read()
        self.result_lp.clear()
        self.result_lp.setFontPointSize(8)
        self.result_lp.setText(file)

        f = os.path.join(pathname, 'result_rp.txt')
        file = open(f,'r').read()
        self.result_rp.clear()
        self.result_rp.setFontPointSize(8)
        self.result_rp.setText(file)

    def Help(self):
        """ Show the short description """
        msg = QMessageBox()
        msg.setWindowTitle("Short description")
        msg.setText("This program is dedicated to measure the antenna temperature "\
        "of the continuum cross-scans (Tianma 65-m telescope). "\
        "------------------------------------------------------------------------------------------------- \n "\
        "Select the directory first. Then in loaded list click to the fits files. "\
        "Gauss-profile will be fitted automatically after baseline and offset corrections. "\
        "The result will be saved to the txt file in the same directory. "\
        "If the gain curve equation is known, it's possible to correct for it as well.")
        retval = msg.exec_()


    def GainCoeff(self):
        """ Read the A, B, C values """
        global A, B, C
        A = float(self.textbox4.text())
        B = float(self.textbox5.text())
        C = float(self.textbox6.text())

    def clickedList(self, item):
        """ 1) read the clicked file
            2) run readdata(), gaussFit() etc for LP and RP """
        global fname, filename
        fname = str(item.text())
        filename = str(pathname+'/'+fname)
        self.readdata()

        ''' # LP '''
        pol = 'LP'
        y = lp
        self.gaussFit(x,y)
        N=1
        self.parameters(r,el,N,pol)
        self.baselineCalc(y)
        self.gaussFit(x,sbtr)
        N=2
        self.parameters(r,el,N,pol)
        self.plotScanLP()
        #self.combineLPresult()

        ''' # RP '''
        pol = 'RP'
        y = rp
        self.gaussFit(x,y)
        N=1
        self.parameters(r,el,N,pol)
        self.baselineCalc(y)
        self.gaussFit(x,sbtr)
        N=2
        self.parameters(r,el,N,pol)
        self.plotScanRP()
        #self.combineRPresult()


    def readdata(self):
        """
        this function reads the fits file
        """
        global source, freq, bw, el, time, rtsys, dec, ra, rp, lp, x, axlbl
        header_table0 = fits.getheader(filename,0)
        source = header_table0['source']
        freq = header_table0['freq']
        bw = header_table0['bw']
        az = header_table0['az']
        el = header_table0['el']
        time = header_table0['time']
        rtsys = header_table0['rtsys']
        data_table, header_table = fits.getdata(filename, 1, header=True)
        dec = data_table.field('DDEC')
        ra = data_table.field('DRA')
        rp = data_table.field('RP')
        lp = data_table.field('LP')
        self.textbox2.clear()
        self.textbox3.clear()
        self.textbox2.setText(source)
        self.textbox3.setText(str(freq))
        if fname[0] == "R":
            x = ra
            axlbl = "RA"
        else:
            x = dec
            axlbl = "Dec"


    def gaussFit(self, a, b):
        """
        this function fits the gauss
        """
        global r
        g_init = models.Gaussian1D(amplitude=1., mean=0, stddev=1.)
        fit_g = fitting.LevMarLSQFitter()
        r = fit_g(g_init, a, b)

    def parameters(self, r,el,N,pol):
        """
        calculate parameters of the gauss fit,
        write results to the textboxes and to the file
        """
        global maximum, sigma, mean, fwhm
        maximum = np.around(r.amplitude.value, decimals=2) # Amplitude Y-coordinate
        fwhm = np.around(2.3548*r.stddev.value, decimals=2) # HPBW
        mean = np.around(r.mean.value, decimals=3) #offset value X-coordinate

        ''' correct Temperature for offset and gain (if coeff. are entered)'''
        off_corr = np.exp(-4.0 * np.log(2.0) * (mean/fwhm)**2.0)

        if 'A' in globals():
            gain = A*el**2 + B*el + C
            T = maximum / (off_corr * gain)
        else:
            T = maximum / off_corr

        ''' write calculated parameters to file '''
        if N==2:
            sigma = np.around(np.sqrt(sum((r(x) - sbtr)**2)/len(r(x))), decimals=3)

            data_rows = [(fname, source, el, time, rtsys, maximum, T, sigma, fwhm, mean)]
            t = Table(rows=data_rows, names=('File', 'Name', 'Elevat', 'Time(MJD)', 'Tsys(K)', 'Max(K)', 'T_oc', 'sigma', 'FWHM', 'Offset'),
                  dtype=('S7', 'S8', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4', 'f4'))
            t['Max(K)'].format = '.3f'
            t['T_oc'].format = '.3f'
            t['Elevat'].format = '.3f'
            t['Time(MJD)'].format = '.3f'
            t['Tsys(K)'].format = '.3f'
            t['FWHM'].format = '.2f'
            t['sigma'].format = '.3f'
            t['Offset'].format = '.2f'
            t.write(str(fname)+'_'+pol+'.txt', format='ascii') #overwrite=True

    def baselineCalc(self, y):
        """ calculating baseline
        xx1, xx2 - left and right borders of the gauss fit
        bb1, bb2 - left and right borders for the baseline calc
        b1, b2 - INDEX of the value closets to border (bb1,bb2)
        xx,yy - sets of two points to use in interpolation
        """
        global bb1, bb2, f, sbtr

        xx1 = mean - fwhm
        if xx1 > 0:
            bb1 = int(fwhm/2 + xx1)
        else:
            bb1 = int(xx1 - fwhm/2)
        xx2 = mean + fwhm
        if xx2 > 0:
            bb2 = int(fwhm/2 + xx2)
        else:
            bb2 = int(xx2 - fwhm/2)


        ''' to know INDEX of the value closets to baseline border in X-array'''
        b1 = min(range(len(x)), key=lambda i: abs(x[i]-bb1))
        b2 = min(range(len(x)), key=lambda i: abs(x[i]-bb2))

        ''' linear interpolation between 2 points (baseline)'''
        yy1 = y[b1]
        yy2 = y[b2]
        xx = (bb1,bb2)
        yy = (yy1,yy2)
        f = interp1d(xx, yy, "linear", bounds_error=False)
        sbtr = y - f(x)
        inds = np.where(np.isnan(sbtr))
        sbtr[inds] = 0


    def plotScanRP(self):
        """
        plot scan, gauss fit, baseline
        """
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> Tant (K) = %0.3f , std = %0.3f, offset (") = %0.1f , HPBW (") = %0.1f </span></div>' % (maximum, sigma, mean, fwhm), anchor=(0,0))
        text.setPos(min(x), max(rp) + max(rp)/20)
        self.pw_RP.clear()
        self.pw_RP.addLegend(size=(2,10), offset=(10, 100))
        self.pw_RP.setTitle(source)
        self.pw_RP.setLabel('left', 'T_ant', units='K')
        self.pw_RP.setLabel('bottom', axlbl, units='arcsec')
        self.pw_RP.plot(x, rp, pen='r', symbol=None, name='raw data')
        self.pw_RP.plot(x, r(x), pen='g', symbol=None, name='gauss fit')
        self.pw_RP.plot(x, f(x), pen='k', symbol=None, name='baseline')
        self.pw_RP.addLine(x=bb1, pen='k')
        self.pw_RP.addLine(x=bb2, pen='k')
        self.pw_RP.addItem(text)
        """ save image as png """
        exporter = pg.exporters.ImageExporter(self.pw_RP.plotItem)
        exporter.parameters()['height'] = 500
        savename = fname.split('.')[0]
        exporter.export(str(fname)+'_RP.png')
        #self.pw_RP.savefig(str(fname)+'.png', bbox_inches='tight')

    def plotScanLP(self):
        """
        plot scan, gauss fit, baseline
        """
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> Tant (K) = %0.3f , std = %0.3f, offset (") = %0.1f , HPBW (") = %0.1f </span></div>' % (maximum, sigma, mean, fwhm), anchor=(0,0))
        text.setPos(min(x), max(lp) + max(lp)/20)
        self.pw_LP.clear()
        self.pw_LP.addLegend(size=None, offset=(10, 100))
        self.pw_LP.setTitle(source)
        self.pw_LP.setLabel('left', 'T_ant', units='K')
        self.pw_LP.setLabel('bottom', axlbl, units='arcsec')
        self.pw_LP.plot(x, lp, pen='r', symbol=None, name='raw data')
        self.pw_LP.plot(x, r(x), pen='g', symbol=None, name='gauss fit')
        self.pw_LP.plot(x, f(x), pen='k', symbol=None, name='baseline')
        self.pw_LP.addLine(x=bb1, pen='k')
        self.pw_LP.addLine(x=bb2, pen='k')
        self.pw_LP.addItem(text)
        """ save image as png """
        exporter = pg.exporters.ImageExporter(self.pw_LP.plotItem)
        exporter.parameters()['height'] = 500
        savename = fname.split('.')[0]
        exporter.export(str(fname)+'_LP.png')

    def combineRPresult(self):
        """
        1) list and identify RA/DEC resulting files
        2) compound resulting files using bash 'cat' procedure,
        3) remove results for individual scans (clean up)
        4) remove extra headings
        """
        allfiles = [i for i in os.listdir('.') if os.path.isfile(i)]
        tempfile = "*RP.txt"
        tempfiles = []

        for name in allfiles:
            if fnmatch(name, tempfile):
               tempfiles.append(name)
        N = len(tempfiles) + 1

        if N > 1:
            system("cat *RP.txt>result_rp.txt")
            system("rm *RP.txt")

        ''' remove extra headings (if they are exist, files > 2)'''
        if N >= 3:
            n = np.arange(2,N,1)
            f=open("result_rp.txt").readlines()
            for i in n:
                f.pop(i)
            with open("result_rp.txt",'w') as F:
                F.writelines(f)

    def combineLPresult(self):
        """
        1) list and identify RA/DEC resulting files
        2) compound resulting files using bash 'cat' procedure,
        3) remove results for individual scans (clean up)
        4) remove extra headings
        """
        allfiles = [i for i in os.listdir('.') if os.path.isfile(i)]
        tempfile = "*LP.txt"
        tempfiles = []

        for name in allfiles:
            if fnmatch(name, tempfile):
               tempfiles.append(name)
        N = len(tempfiles) + 1

        if N > 1:
            system("cat *LP.txt>result_lp.txt")
            system("rm *LP.txt")

        ''' remove extra headings (if they are exist, files > 2)'''

        if N >= 3:
            n = np.arange(2,N,1)
            f=open("result_lp.txt").readlines()
            for i in n:
                f.pop(i)
            with open("result_lp.txt",'w') as F:
                F.writelines(f)

    def clearResult(self):
        """
        clear resulting files (if you don't want to save files)
        """
        allfiles = [i for i in os.listdir('.') if os.path.isfile(i)]
        tempfile_r = "R*P.txt"
        tempfiles_r = []
        tempfile_d = "D*P.txt"
        tempfiles_d = []
        for name in allfiles:
            if fnmatch(name, tempfile_r):
               tempfiles_r.append(name)
            if fnmatch(name, tempfile_d):
               tempfiles_d.append(name)
        N_d = len(tempfiles_d)
        N_r = len(tempfiles_r)
        if N_d >= 1:
            system("rm D*P.txt")
        if N_r >= 1:
            system("rm R*P.txt")

        #self.showRes()


def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
