from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QRunnable, QThread, QThreadPool, pyqtSignal, QDir
import datetime as dt
import serial
import pyqtgraph
import sys
import glob
import csv
import os.path
import utilities as ut

class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('gui.ui', self)

        # Inits and populates the box with available COM Ports
        self.cbox = self.comboBox_COM
        self.portScanner()

        # Sets up the browse for write-to file button (CSV)
        # self.buttonBrowse.clicked.connect(self.buttonBrowse_clicked)

        # connect the length value changed to the length update function
        #self.slideLength.valueChanged.connect(self.slideLength_changed)

        # init's the data logger for the csv file writing
        #self.log = ut.Logger()
        #self.buttonSerialOpen.clicked.connect(self.log.openLogFile)

        # Sets up the serial port stream
        self.stream = ut.Streamer(dataHandler=self.parseResponse)
        #self.stream.newdata.connect(self.log.writeLine)
        self.buttonSerialOpen.clicked.connect(self.buttonSerialOpen_clicked)
        self.buttonSerialSend.clicked.connect(self.buttonSerialSend_clicked)

        self.show()

    def buttonSerialOpen_clicked(self, port):
        self.stream.changePort(str(self.cbox.currentText()))
        self.stream.start()

    def buttonSerialSend_clicked(self):
        self.stream.sendCommand(self.lineEdit_Command.text())

    def portScanner (self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.cbox.addItem(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def parseResponse(self, text):
        print(text)

def initGui():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.setWindowTitle("Windrunner Test GUI")
    #window.setWindowIcon(QtGui.QIcon("icon.jpg"))
    window.show()
    app.exec_()
