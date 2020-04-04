from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QRunnable, QThread, QThreadPool, pyqtSignal, QDir
import datetime as dt
import serial
import csv
import os.path

class Streamer(QThread):
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM7'

    newdata = pyqtSignal(str)

    def __init__(self, dataHandler):
        super(Streamer, self).__init__()
        self.newdata.connect(dataHandler)

    def changePort(self, port):
        self.ser.port = port

    def sendCommand(self, text):
        b = bytearray()
        b.extend(map(ord, text))
        self.ser.write(b)

    def run(self):
        try:
            self.ser.open()
        except:
            print("Port Unavailable!")

        while True:
            if self.ser.in_waiting:
                msg = str(self.ser.readline())
                self.newdata.emit(msg)

        self.ser.close()

class Logger(QThread):

    csvFolder = None
    csvFile = None
    filewriter = None

    def __init__(self):
        super(Logger, self).__init__()

    def setLogFolder(self, folder):
        self.csvFolder = folder

    def openLogFile(self):
        if self.csvFolder:
            i = 0

            while os.path.isfile(self.csvFolder + '/' + 'capLog' + str(i).zfill(4) + '.csv')  and i < 4096:
                i += 1

            self.csvFile = self.csvFolder + '/' + 'capLog' + str(i).zfill(4) + '.csv'
            with open(self.csvFile, 'w', newline='') as file:
                self.filewriter = csv.writer(file)
                self.filewriter.writerow(['Electrode 1', 'Electrode 2', 'Electrode 3', 'Electrode 4', 'Electrode 5',
                                     'Timestamp'])

    def writeLine(self, list):
        if self.csvFile:
            newList = [str(i) for i in list]
            newList.append(dt.datetime.now().strftime('%d/%m/%Y %H:%M:%S.%f'))
            with open(self.csvFile, 'a', newline='') as file:
                self.filewriter = csv.writer(file)
                self.filewriter.writerow(newList)