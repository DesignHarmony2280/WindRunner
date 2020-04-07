from PyQt5.QtCore import QThread, pyqtSignal
import serial
import sys
import glob

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
                msg = str(self.ser.readline())
                self.newdata.emit(msg)

        self.ser.close()


class Rover:

    def __init__(self):
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

