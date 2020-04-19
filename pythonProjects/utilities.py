from PyQt5.QtCore import QThread, QObject, pyqtSignal
import serial
import sys
import glob

'''
Class: Streamer

Provides all of the necessary functions to deal with a COM port on Linux or Windows systems, as well as send commands
to a Rover class item.
'''
class Streamer(QThread):
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM7'

    newdata = pyqtSignal(bytearray)

    def __init__(self, dataHandler):
        super(Streamer, self).__init__()
        self.newdata.connect(dataHandler)

    '''
    Changes the serial port to that specified
    '''
    def changePort(self, port):
        self.ser.port = port

    '''
    Simply writes a text command over the serial port to a Rover Class Item
    '''
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

    '''
    Scans the host device to find all available serial ports, returns a list of the names of each port.
    '''
    def portScan (self):

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
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def run(self):
        try:
            self.ser.open()
        except:
            print("Port Unavailable!")

        while True:
            if self.ser.in_waiting:
                self.ser.flush()
                msg = bytearray(self.ser.readline())
                self.newdata.emit(msg)

        self.ser.close()


class Rover(QObject):

    # Signal Definitions - See manual for handling instructions...
    driveResponse = pyqtSignal(int)
    positionResponse = pyqtSignal(list)
    orientationResponse = pyqtSignal(list)
    sensorResponse = pyqtSignal(list)

    def __init__(self):
        super(Rover, self).__init__()
        pass

    '''
    Rover constructor which allows the passing of handler functions for when the windrunner sends valid commands back
    '''
    def __init__(self, driveHandler, positionHandler, orientationHandler, sensorHandler):
        super(Rover, self).__init__()
        self.driveResponse.connect(driveHandler)
        self.positionResponse.connect(positionHandler)
        self.orientationResponse.connect(orientationHandler)
        self.sensorResponse.connect(sensorHandler)
        pass

    def createSendDriveCmd(self, direction, duration, speed):

        """
        Function takes in below described arguments and returns a bytearray with the
        ASCII Data necessary to command the Windrunner Rover to complete the given
        command.

        :param direction:
        :param duration:
        :param speed:
        :return: ASCII Bytearray Command
        """

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

    def createSendPosCmd(self):

        """
        Function returns a bytearray command which will request the rover to send positional data as described in
        the MAN.md file.

        :return: ASCII Bytearray Command
        """

        return bytearray("$10", 'ascii')

    def createSendOriCmd(self):

        """
        Function returns a bytearray command which will request the rover to send orientation data as described in
        the MAN.md file.

        :return: ASCII Bytearray Command
        """

        return bytearray("$20", 'ascii')

    def createSendSenseCmd(self):

        """
        Function returns a bytearray command which will request the rover to send orientation data as described in
        the MAN.md file.

        :return: ASCII Bytearray Command
        """

        return bytearray("$30", 'ascii')

    '''
    Parses an incoming text string for data from the windrunner rover.
    '''
    def parseResponse(self, text):

        if(text[0] == 36):  # If '$' is received
            if(text[1] == 48):      # If CMD == 0
                self.driveResponse.emit(text[3])
            elif(text[1] == 49):    # If CMD == 1
                lat = 0
                lon = 0
                for i in range(3,6):
                    lat = (lat*256) + text[i]
                for i in range(7,10):
                    lon = (lon*256) + text[i]
                self.positionResponse.emit([lat, lon])
            elif(text[1] == 50):    # If CMD == 2
                x = text[3]*256 + text[4]
                y = text[5]*256 + text[6]
                z = text[7]*256 + text[8]
                self.orientationResponse.emit([x,y,z])
            elif(text[1] == 51):    # If CMD == 3
                wind = (int(text[3])/256)*32.4
                light = (int(text[4])/256)*6000
                temp = (int(text[5])/256)*100
                self.sensorResponse.emit([wind, light, temp])
        else:
            print(text)