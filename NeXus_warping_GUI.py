"""GUI for k-Warping NeXus files. The GUI takes in an input file, outputs to the selected destination.
The kx and ky pixel fields are compulsory. The offsets and workfunction are optional.
The code will output a new NeXus file containin the kWarped 3D datacube, the values of the axes, kinetic, kx, ky and binding energy
(binding energy is -KE if work function is zero)."""

import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import (QPushButton, QApplication, QLineEdit)
from PyQt5.QtWidgets import (QWidget)
from PyQt5 import QtCore
import h5py
from nexusformat.nexus import *

class Second(QtWidgets.QDialog):
    def __init__(self, parent=None):
        global v1, v2, v3, v4, open1, programtype   # Set global parameters now so they can be changed when OK is hit
        v1 = ''
        v2 = ''
        v3 = ''
        v4 = ''
        open1 = ''
        programtype = ''

        super(Second, self).__init__(parent)
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setGeometry(370, 250, 550, 250)    # Set size and positioning of window
        self.setWindowTitle('Advanced Options')

        title = QtWidgets.QLabel(self)
        title.setText(
            "If your file does not match any of the available formats, you can input the direct paths to the arrays here.")
        title.move(12, 10)

        information = QtWidgets.QLabel(self)
        information.setText("The paths should be in a form similar to: /entry1/instrument/analyser/data")
        information.move(12, 28)

        data = QtWidgets.QLabel(self)
        data.setText("Enter 3D intensity datacube path:")
        data.move(20, 60)
        self.data = QLineEdit(self)     # 3D Datacube path input
        self.data.move(200, 60)

        energies = QtWidgets.QLabel(self)
        energies.setText("Enter 1D energy array path")
        energies.move(20, 90)
        self.energies = QLineEdit(self)     # 1D Energy path input
        self.energies.move(200, 90)

        angles = QtWidgets.QLabel(self)
        angles.move(20, 120)
        angles.setText("Enter 1D angles (theta) array path:")
        self.angles = QLineEdit(self)
        self.angles.move(200, 120)

        anapolar = QtWidgets.QLabel(self)
        anapolar.move(20, 150)
        anapolar.setText("Enter 1D anapolar array path:")
        self.anapolar = QLineEdit(self)
        self.anapolar.move(200, 150)

        # Click OK to pass the new paths to the main window
        self.hi = QPushButton('OK', self)
        self.hi.move(18, 200)
        self.hi.resize(self.hi.sizeHint())
        self.hi.clicked.connect(self.OK_hit)

        # Cancel just closes the dialog box
        self.OK = None
        self.cancel = QPushButton('Cancel', self)
        self.cancel.move(100, 200)
        self.cancel.resize(self.cancel.sizeHint())
        self.cancel.clicked.connect(self.OK_hit)

    # Passes the new paths as variables to the main window
    def OK_hit(self):
        QtWidgets.QDialog.close(self)
        global v1, v2, v3, v4
        v1 = self.data.text()
        v2 = self.energies.text()
        v3 = self.angles.text()
        v4 = self.anapolar.text()

    def cancel_hit(self):
        QtWidgets.QDialog.close(self)

class Third(QtWidgets.QDialog):
    """ This class creates a dialog box which displays the NeXus tree"""
    def __init__(self, parent=None):
        super(Third, self).__init__(parent)
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setGeometry(370, 250, 300, 300)
        self.setWindowTitle('Tree Display')

        self.hi1 = QPushButton('OK', self)
        self.hi1.move(12, 265)
        self.hi1.resize(self.hi1.sizeHint())
        self.hi1.clicked.connect(self.OK_hit1)

        self.cancel1 = QPushButton('Cancel', self)
        self.cancel1.move(92, 265)
        self.cancel1.resize(self.cancel1.sizeHint())
        self.cancel1.clicked.connect(self.OK_hit1)

        b0 = QPushButton('Select Input File', self)
        b0.setToolTip('Select the .nxs file to be warped')
        b0.resize(b0.sizeHint())
        b0.move(12, 12)
        b0.clicked.connect(self.b0_clicked)

        self.lez = QLineEdit(self)
        self.lez.move(112, 12)

        info = QtWidgets.QLabel(self)
        info.setText("Suggested Program:")
        info.move(12,243)
        self.suggested = QLineEdit(self)
        self.suggested.move(120,240)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.move(12,45)

    def b0_clicked(self):
        """Takes in an input file and returns the NeXus tree, suggests program name"""
        self.openz = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.lez.setText(self.openz)
        fileName = self.openz
        texty = nxload(fileName).tree
        self.text_edit.setText(texty)

        if "program_name" in texty:
            prog = texty.index("program_name")
            self.suggested.setText(texty[prog+15:prog+30])


    def OK_hit1(self):
        QtWidgets.QDialog.close(self)

    def cancel_hit1(self):
        QtWidgets.QDialog.close(self)

class First(QWidget):
    """ Main Class, defines a Widget which takes in the necessary variables"""
    def __init__(self, parent=None):
        super(First, self).__init__(parent)
        global open1
        open1 = ''
        self.nd = Second(self)
        self.nd1 = Third(self)

        b = QtWidgets.QLabel(self)
        b.setText(
            "This program will take in an .nxs file and transform the data from (phi, theta, E) to (kx, ky, E).")
        b.move(12, 10)

        self.b6 = QtWidgets.QLabel(self)
        self.b6.setText(
            "View the file structure using 'Tree' below. The version is stored under the heading 'program_name'.")
        self.b6.move(12, 35)
        self.b61 = QtWidgets.QLabel(self)
        self.b61.setText(
            "If your version is not displayed below, manually input the paths to the arrays using the 'User Defined' option.")
        self.b61.move(12, 50)

        b7 = QtWidgets.QLabel(self)
        b7.setText("Program Version:")
        b7.move(12, 145)
        self.pushButton = QtWidgets.QPushButton("User Defined", self)
        self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton.move(200, 140)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #                                                                           #
        #      This section should be adapted when new versions are implemented     #
        #                                                                           #
        #          Add new lines of self.comboBox.addItem("GDA.X.X.X")              #
        #                                                                           #
        #      Change the choice names 'GDA X.X.X.' to the relevant versions        #
        #                                                                           #
        #  Also adapt 'if choice == 'GDA.X.X.X.'' statements in other kWarpingfile  #
        #                                                                           #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.addItem("GDA 8.52.0")
        self.comboBox.addItem("GDA 9.1.0")
        self.comboBox.addItem("User Defined")
        self.comboBox.setObjectName('__qt__passive_comboBox')
        self.stackWidget = QtWidgets.QStackedWidget()
        self.comboBox.move(103, 142)
        self.comboBox.setToolTip(
            'Select the version which matches the structure of your nxs file. If incorrect the process will terminate.')

        b1 = QPushButton('Select Input File', self)
        b1.setToolTip('Select the .nxs file to be warped')
        b1.resize(b1.sizeHint())
        b1.move(12, 80)
        b1.clicked.connect(self.b1_clicked)

        self.le = QLineEdit(self)
        self.le.move(112, 81)

        qbtn1 = QPushButton('Tree Display', self)
        qbtn1.clicked.connect(self.tree)
        qbtn1.resize(qbtn1.sizeHint())
        qbtn1.move(280, 80)

        b2 = QPushButton('Save Output As', self)
        b2.move(12, 105)
        b2.clicked.connect(self.b2_clicked)
        b2.setToolTip('Select the destination for the warped file. Please save as filename.nxs')
        b2.resize(b2.sizeHint())
        self.le1 = QLineEdit(self)
        self.le1.move(112, 106)

        # Start taking in the variables to pass to NeXus_kWarping.py
        # Ideally want to adapt this pixels section to calculate optimal number of pixels and suggest this as a maximum

        kxlabel = QtWidgets.QLabel(self)
        kxlabel.setText("Number of kx pixels:")
        kxlabel.move(12, 180)
        self.kxpixels = QtWidgets.QSpinBox(self)
        self.kxpixels.move(120, 177)
        self.kxpixels.setMaximum(1000)
        self.kxpixels.setToolTip('Set the number of kx pixels. Should be less than ky pixels.')


        kylabel = QtWidgets.QLabel(self)
        kylabel.setText("Number of ky pixels:")
        kylabel.move(12, 210)
        self.kypixels = QtWidgets.QSpinBox(self)
        self.kypixels.move(120, 207)
        self.kypixels.setMaximum(1000)
        self.kypixels.setToolTip('Set the number of ky pixels. Should be greater than kx pixels.')

        self.a_correc = QtWidgets.QDoubleSpinBox(self)
        a_correclabel = QtWidgets.QLabel(self)
        self.a_correc.setSingleStep(0.01)
        self.a_correc.setMaximum(360)
        self.a_correc.setMinimum(-360)
        a_correclabel.setText("Gamma position along analyser in A<sup>-1</sup> (i.e. thetax) : ")
        self.a_correc.setToolTip("Leave as default (zero) if unknown.")
        a_correclabel.move(12, 240)
        self.a_correc.move(270, 237)
        self.a_correc.setMaximum(1000)

        self.d_correc = QtWidgets.QDoubleSpinBox(self)
        self.d_correc.setSingleStep(0.01)
        self.d_correc.setToolTip("Leave as default (zero) if unknown.")
        self.d_correc.setMaximum(360)
        self.d_correc.setMinimum(-360)
        d_correclabel = QtWidgets.QLabel(self)
        d_correclabel.setText("Deflector angle Gamma position in A<sup>-1</sup> (i.e. thetay) : ")
        d_correclabel.move(12, 270)
        self.d_correc.move(270, 267)

        self.workfunc = QtWidgets.QDoubleSpinBox(self)
        workfunctionlabel = QtWidgets.QLabel(self)
        workfunctionlabel.setText("*will output a list of binding energies if non-zero")
        workfunctionlabel.move(280,302)
        workfunc = QtWidgets.QLabel(self)
        workfunc.setText("Fermi Energy in eV * (if known) : ")
        workfunc.move(12, 300)
        self.workfunc.move(175, 297)
        self.workfunc.setMaximum(100000)
        self.workfunc.setMinimum(-100000)

        upload = QPushButton('Run Program', self)
        upload.move(30, 340)
        upload.clicked.connect(QCoreApplication.instance().quit)

        qbtn = QPushButton('Cancel', self)
        qbtn.clicked.connect(self.qbtn_clicked)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(110, 340)


        self.setGeometry(320, 200, 550, 380)
        self.setWindowTitle('kWarping nxs files')

    def b1_clicked(self):
        self.open = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.le.setText(self.open)
        open1 = self.le.text()

    def qbtn_clicked(self):
        print("Program terminated.")
        sys.exit()

    def b2_clicked(self):
        self.save = QtWidgets.QFileDialog.getSaveFileName(self, filter='.nxs')[0]
        if self.save.endswith('.nxs') == True:
            self.le1.setText(self.save)
        else:
            self.save1 = self.save + '.nxs'
            self.le1.setText(self.save+ '.nxs')

    def on_pushButton_clicked(self):
        self.nd.show()

    def tree(self):
        self.nd1.show()

def demo_QButton():
    """Runs the entire code, loads Main window and loops continuously; returns the necessary variables for kWarping"""
    app = QApplication(sys.argv)
    tb = First()
    tb.show()
    app.exec_()
    return [tb.le.text(), tb.kxpixels.value(), tb.kypixels.value(), tb.a_correc.value(), tb.d_correc.value(),
                tb.workfunc.value(), tb.le1.text(), tb.comboBox.itemText(tb.comboBox.currentIndex()), v1, v2,
                v3, v4, programtype]

'''Define all the variables to pass into NeXus_kWarping.py'''
variables = demo_QButton()
filename = variables[0]
kxpixels = variables[1]
kypixels = variables[2]
gammaoff1 = variables[3]
gammaoff2 = variables[4]
workfunction = variables[5]
save = variables[6]
choice = variables[7]
datapath = variables[8]
energypath = variables[9]
anglespath = variables[10]
anapolarpath = variables[11]
