from PyQt5 import QtWidgets, QtGui, uic
import sys
import utilities as ut

class Ui(QtWidgets.QMainWindow):

    boxText = ""
    comPorts = []

    def __init__(self):
        super(Ui, self).__init__()
        # Loads up the Qt gui design from designer.
        uic.loadUi('gui.ui', self)

        # Instantiates the rover class with the proper data handlers
        self.rover = ut.Rover(driveHandler=self.updateDriveStatus, positionHandler=self.updatePositionStatus,
                              orientationHandler=self.updateOrientationStatus, sensorHandler=self.updateSensorStatus)

        # Inits and populates the box with available COM Ports
        self.cbox = self.comboBox_COM

        # Sets up the serial port stream
        self.stream = ut.Streamer(dataHandler=self.rover.parseResponse)
        # Populates the COM Port list with the available COM ports
        self.comPorts = self.stream.portScan()

        # Adds all COM Ports to the combo box
        for x in self.comPorts:
            self.comboBox_COM.addItem(x)

        # Sets up all of the necessary signal -> slot connections for the GUI buttons
        self.buttonSerialOpen.clicked.connect(self.buttonSerialOpen_clicked)
        self.buttonSerialSend.clicked.connect(self.buttonSerialSend_clicked)
        self.buttonDriveSend.clicked.connect(self.buttonDriveSend_clicked)
        self.buttonGetSense.clicked.connect(self.buttonGetSense_clicked)
        self.buttonGetPos.clicked.connect(self.buttonGetPos_clicked)
        self.buttonGetOri.clicked.connect(self.buttonGetOri_clicked)

        # Sets up the status box
        self.textRxComm.setPlainText(self.boxText)

        # Shows the GUI
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

    def buttonGetSense_clicked(self):
        self.stream.sendCommand(self.rover.createSendSenseCmd())

    def buttonGetPos_clicked(self):
        self.stream.sendCommand(self.rover.createSendPosCmd())

    def buttonGetOri_clicked(self):
        self.stream.sendCommand(self.rover.createSendOriCmd())

    # The following functions exist as slots to allow incoming data from the rover class to be handled in this thread
    def updateDriveStatus(self, code):
        if code == 0:
            self.updateText("Drive Command Successful")
        elif code == 1:
            self.updateText("Drive Error Occurred")

    def updatePositionStatus(self, vals):
        print(vals)

    def updateOrientationStatus(self, val):
        print(val)

    def updateSensorStatus(self, vals):
        print(vals)
    # ---------------------------------------------------------------------------------------------------------------

def initGui():
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.setWindowTitle("Windrunner Test GUI")
    window.setWindowIcon(QtGui.QIcon("sun.jpg"))
    window.setFixedSize(window.size())
    window.show()
    app.exec_()
