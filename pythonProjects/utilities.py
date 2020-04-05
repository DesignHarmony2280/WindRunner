from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, QRunnable, QThread, QThreadPool, pyqtSignal, QDir
import datetime as dt
import serial
from serial.serialutil import portNotOpenError
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
        if type(text) != bytearray:
            b = bytearray()
            b.extend(map(ord, text))
            try:
                self.ser.write(b)
            except:
                print("Serial Port not yet opened!")
        else:
            try:
                self.ser.write(text)
            except:
                print("Serial Port not yet opened!")

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


class Rover:

    def __init__(self):
        pass

    def createSendDriveCmd(self, direction, duration, speed):
        cmd = bytearray("$0", 'ascii')
        len = 7
        cmd += (len + 48).to_bytes(1, 'big')

        if direction == 'backward':
            cmd += (48).to_bytes(1, 'big')
        elif direction == 'left':
            cmd += (49).to_bytes(1, 'big')
        elif direction == 'right':
            cmd += (50).to_bytes(1, 'big')
        elif direction == 'forward':
            cmd += (51).to_bytes(1, 'big')

        cmd += speed.to_bytes(1, 'big')
        cmd += duration.to_bytes(2, 'big')
        return cmd

