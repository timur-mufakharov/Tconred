#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
from PyQt4.QtGui import *
import pyqtgraph as pg
import numpy as np
from numpy import sqrt, pi, exp, linspace

class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()

        self.setStyleSheet('font-size: 10pt;') # font-family: Courier;

        self.initUI()


    def initUI(self):

        ## Set grid layout
        grid = QGridLayout()
        #grid.setSpacing(10)
        self.setLayout(grid)
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        ## X, Y positions and x,y size of the window
        self.setGeometry(300, 300, 900, 600)
        self.setWindowTitle('Parameters of calibrators')
        self.move(300, 300)

        ''' Create Buttons'''
        button1 = QPushButton('Load file')
        #button1.resize(70, 35)
        button1.clicked.connect(self.showDialog)
        button1.setShortcut('Ctrl+O')
        button2 = QPushButton('Plot gain')
        button2.clicked.connect(self.plotGain)
        button3 = QPushButton('Plot HPBW')
        button3.clicked.connect(self.plotHPBW)
        button4 = QPushButton('Plot Tsys-MJD')
        button4.clicked.connect(self.plotTsysMJD)
        button5 = QPushButton('Plot offsets')
        button5.clicked.connect(self.plotOffsets)
        button6 = QPushButton('Plot Tsys-Elev')
        button6.clicked.connect(self.plotTsysEl)
        lbl1 = QLabel('Selected file')
        lbl2 = QLabel('average value =')
        lbl3 = QLabel('std deviation =')
        lbl4 = QLabel('Source name')
        lbl_g = QLabel('Gain equation')
        lbl_g1 = QLabel('A =')
        lbl_g2 = QLabel('B =')
        lbl_g3 = QLabel('C =')
        lbl_res = QLabel('residuals =')
        self.textbox1 = QLineEdit() #selected file
        self.textbox2 = QLineEdit() #average
        self.textbox3 = QLineEdit() #std
        self.textbox4 = QLineEdit() #source name
        self.textbox_g1 = QLineEdit() #A
        self.textbox_g2 = QLineEdit() #B
        self.textbox_g3 = QLineEdit() #C
        self.textbox_res = QLineEdit() #residuals
        self.pw = pg.PlotWidget()

        ''' Locate widgets '''
        grid.addWidget(button1, 1, 0)
        grid.addWidget(button2, 2, 0)
        grid.addWidget(button3, 3, 0)
        grid.addWidget(button4, 4, 0)
        grid.addWidget(button5, 3, 1)
        grid.addWidget(button6, 4, 1)
        grid.addWidget(lbl1, 6, 0)
        grid.addWidget(lbl4, 8, 0)
        grid.addWidget(lbl2, 9, 0)
        grid.addWidget(lbl3, 10, 0)
        grid.addWidget(lbl_g, 11, 0)
        grid.addWidget(lbl_g1, 12, 0)
        grid.addWidget(lbl_g2, 13, 0)
        grid.addWidget(lbl_g3, 14, 0)
        grid.addWidget(lbl_res, 15, 0)
        grid.addWidget(self.textbox1, 7, 0, 1, 2)
        grid.addWidget(self.textbox2, 9, 1)
        grid.addWidget(self.textbox3, 10, 1)
        grid.addWidget(self.textbox4, 8, 1)
        grid.addWidget(self.textbox_g1, 12, 1)
        grid.addWidget(self.textbox_g2, 13, 1)
        grid.addWidget(self.textbox_g3, 14, 1)
        grid.addWidget(self.textbox_res, 15, 1)
        grid.addWidget(self.pw, 1, 2, 15, 1)

        self.show()


    def showDialog(self):
        global fname
        fname = str(QFileDialog.getOpenFileName(self, 'Open file', '/home/Desktop/pyqt_start'))
        f = open(fname, 'r')
        with f:
            data = f.read()
            self.textbox1.setText(fname)
            dat=np.genfromtxt(fname, missing_values='n', dtype=None, skip_header=1)
            source=dat[1][1]
            self.textbox4.setText(source)


    def plotHPBW(self):
        data1=np.genfromtxt(fname, missing_values='n', skip_header=1)
        fwhm1=data1[:,8]
        aver1 = np.around(np.mean(fwhm1), decimals=2)
        std1 = np.around(np.std(fwhm1, ddof=1), decimals=2)
        bins = np.arange(aver1-15,aver1+15,1) #np.linspace(100,200,10)
        y,x = np.histogram(fwhm1, bins=bins)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 128))
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> HPBW (arcsec) = %0.2f , std = %0.2f </span></div>' % (aver1,std1), anchor=(0,0))
        text.setPos(min(x), max(y))
        self.pw.clear()
        self.pw.setTitle('Half Power Beam Widths distribution')
        self.pw.addLegend()
        self.pw.setLabel('left', 'Number')
        self.pw.setLabel('bottom', 'HPBW', units='arcsec')
        self.pw.addItem(curve)
        self.pw.addItem(text)
        self.textbox2.setText(str(aver1))
        self.textbox3.setText(str(std1))


    def plotOffsets(self):
        data1=np.genfromtxt(fname, missing_values='n', skip_header=1)
        el1=data1[:,2]
        off1=abs(data1[:,9])
        aver1 = np.around(np.mean(off1), decimals=2)
        std1 = np.around(np.std(off1), decimals=2)
        bins = np.arange(aver1-10,aver1+10,1) #np.linspace(100,200,10)
        y,x = np.histogram(off1, bins=bins)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 128))
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> Offset (arcsec) = %0.2f , std = %0.2f </span></div>' % (aver1,std1), anchor=(0,0))
        text.setPos(min(x), max(y))
        self.pw.clear()
        self.pw.addLegend()
        self.pw.setTitle('Offsets distribution (absolute values)')
        self.pw.setLabel('left', 'Number')
        self.pw.setLabel('bottom', 'Offset', units='arcsec')
        #self.pw.addLine(x=0)
        #self.pw.plot(el1, off1, pen=None, symbol='o')
        self.pw.addItem(curve)
        self.pw.addItem(text)
        self.textbox2.setText(str(aver1))
        self.textbox3.setText(str(std1))

    def plotTsysMJD(self):
        data1=np.genfromtxt(fname, missing_values='n', skip_header=1)
        time1=data1[:,3]
        temp1=data1[:,4]
        aver1 = np.around(np.mean(temp1), decimals=2)
        std1 = np.around(np.std(abs(temp1)), decimals=2)
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> Taver (K) = %0.4f , std = %0.4f </span></div>' % (aver1,std1), anchor=(0,0))
        text.setPos(min(time1), max(temp1))
        self.pw.clear()
        self.pw.addLegend()
        self.pw.setTitle('Tsys')
        self.pw.setLabel('left', 'Tsys', units='K')
        self.pw.setLabel('bottom', 'Time', units='MJD')
        self.pw.plot(time1, temp1, pen=None, symbol='o')
        self.pw.addItem(text)
        self.textbox2.setText(str(aver1))
        self.textbox3.setText(str(std1))

    def plotTsysEl(self):
        data1=np.genfromtxt(fname, missing_values='n', skip_header=1)
        el1=data1[:,2]
        temp1=data1[:,4]
        aver1 = np.around(np.mean(temp1), decimals=2)
        std1 = np.around(np.std(abs(temp1)), decimals=2)
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> Taver (K) = %0.4f , std = %0.4f </span></div>' % (aver1,std1), anchor=(0,0))
        text.setPos(min(el1), max(temp1))
        self.pw.clear()
        self.pw.addLegend()
        self.pw.setTitle('Tsys')
        self.pw.setLabel('left', 'Tsys', units='K')
        self.pw.setLabel('bottom', 'Elevation', units='deg')
        self.pw.plot(el1, temp1, pen=None, symbol='o')
        self.pw.addItem(text)
        self.textbox2.setText(str(aver1))
        self.textbox3.setText(str(std1))

    def plotGain(self):
        data1=np.genfromtxt(fname, missing_values='n', skip_header=1)
        #source=data1[2][1]
        el1=data1[:,2]
        t1=data1[:,6]
        rms1=data1[:,7]
        gain1 = t1/max(t1)
        error1 = rms1/t1
        err = pg.ErrorBarItem(x=el1, y=gain1, height=error1)
        ''' fit polynom '''
        z, res, _, _, _ = np.polyfit(el1, gain1, 2, full = True)
        p = np.poly1d(z)
        xp = np.arange(10,90,1)
        a = np.around(z[0], decimals=4)
        b = np.around(z[1], decimals=4)
        c = np.around(z[2], decimals=4)
        text = pg.TextItem(html='<div style="text-align:center"><span style="color:red; font-size:8pt;"> y=%0.4f *x^2+ %0.4f *x+ %0.4f </span></div>' % (a,b,c), anchor=(0,0))
        text.setPos(10, 0.99)
        ''' plot '''
        self.pw.clear()
        self.pw.addLegend()
        self.pw.setTitle('Gain curve')
        self.pw.setLabel('left', 'T/T_max')
        self.pw.setLabel('bottom', 'Elevation', units='deg')
        self.pw.plot(el1, gain1, pen=None, symbol='o')
        self.pw.plot(xp, p(xp), pen='r', symbol=None) #name='polyfit'
        self.pw.addItem(err)
        self.pw.addItem(text)
        ''' write to textbox (A,B.C)'''
        self.textbox_g1.setText(str(a))
        self.textbox_g2.setText(str(b))
        self.textbox_g3.setText(str(c))
        self.textbox_res.setText(str(res))


def main():

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
