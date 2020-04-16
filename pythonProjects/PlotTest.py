from PyQt5 import QtWidgets, QtGui, uic
import sys
import utilities as ut

class Ui(QtWidgets.QMainWindow):

    boxText = ""
    comPorts = []

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('gui.ui', self)

        self.rover = ut.Rover()

        # Inits and populates the box with available COM Ports
        self.cbox = self.comboBox_COM

        # Sets up the serial port stream
        self.stream = ut.Streamer(dataHandler=self.parseResponse)
        self.comPorts = self.stream.portScan()

        for x in self.comPorts:
            self.comboBox_COM.addItem(x)

        self.buttonSerialOpen.clicked.connect(self.buttonSerialOpen_clicked)
        self.buttonSerialSend.clicked.connect(self.buttonSerialSend_clicked)
        self.buttonDriveSend.clicked.connect(self.buttonDriveSend_clicked)

        self.textRxComm.setPlainText(self.boxText)

        self.show()

    def buttonSerialOpen_clicked(self, port): #todo: Figure out why this causes crashes...
        self.stream.changePort(str(self.cbox.currentText()))
        try:
            self.stream.start()
            self.updateText("Serial Port Opened!")
        except: #todo: create closeout and reopen procedure.
            self.updateText("Restart for Port Change.")

    def updateText(self, newstr):
        self.boxText += newstr + "\n"
        self.textRxComm.setPlainText(self.boxText)

    def buttonSerialSend_clicked(self):
        self.stream.sendCommand(self.lineEdit_Command.text())
        self.updateText("Command Sent: " + self.lineEdit_Command.text())

    def buttonDriveSend_clicked(self):
        self.stream.sendCommand(self.rover.createSendDriveCmd(direction=str(self.comboBox.currentText()),
                                                              duration=int(self.lineDriveDuration.text()),
                                                              speed=int(self.lineDriveSpeed.text())))

        self.updateText("Drive Command Sent")

    def parseResponse(self, text):

        if(text[0] == 36):  # If '$' is received
            if(text[1] == 48):      # If CMD == 0
                if(text[3] == 1):
                    self.updateText("Drive Command Successful")
                else:
                    self.updateText("Error")
            elif(text[1] == 49):    # If CMD == 1
                print("Orientation Command Received")
            elif(text[2] == 50):    # If CMD == 2
                print("Compass Command Received")
            elif(text[3] == 51):    # If CMD == 3
                print("Sensor Command Received")

def initGui():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.setWindowTitle("Windrunner Test GUI")
    window.setWindowIcon(QtGui.QIcon("sun.jpg"))
    window.setFixedSize(window.size())
    window.show()
    app.exec_()
