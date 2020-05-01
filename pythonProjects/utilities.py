from PyQt5.QtCore import QThread, QObject, pyqtSignal
import serial
from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import glob
import typing
import time
import os

# Storage of Sensor Data
latitude: typing.List = []
longitude: typing.List = []
orientation: typing.List = [0]
temperature: typing.List = []
light_intensity: typing.List = []
wind_speed: typing.List = []

# For 3D Plotting
row_length: int = 0
col_length: int = 0


def generateVisualization(data: typing.List, label: str, output_path: str, plt_type: str):
    """
    Generates visualizations of the sensor data for the web page. Return the file path of the image
    Note: Due to low sensitivity of lat/long position, the sensor data is graphed against index values
    :param data: 2D array of input data
    :param label: Sensor data type
    :param output_path: Directory of output images
    :param plt_type: Type of plot to be generated (i.e. 2D or 3D)
    :return: File path of the image
    """

    # Generate random update name (Note: "Random" name is needed to force an update for the webpage image)
    output_name = output_path + label + "_" + str(int(time.time())) + ".png"

    if plt_type == "2D":
        data_df = pd.DataFrame(data, columns=[label])
        data_df["Location"] = range(data_df.shape[0])

        plot = sns.scatterplot(
            x="Location",
            y=label,
            data=data_df,
            marker=".",
            linewidth=0,
            color="blue"
        ).set_title(f"{label} vs Location")

        fig = plot.get_figure()

    elif plt_type == "3D":
        # Generate grid indices
        x = []
        row_idx = 0
        while len(x) < len(data):
            x = x + [row_idx] * col_length
            row_idx += 1
        while len(x) > len(data):
            x.pop()

        y = []
        j_1 = list(range(col_length))
        j_2 = list.copy(j_1)
        list.reverse(j_2)
        while len(y) < len(data):
            y = y + j_2 + j_1
        while len(y) > len(data):
            y.pop()

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        ax.set_zlabel(label)
        plt.xticks(range(row_length))
        plt.yticks(range(col_length))
        ax.scatter(x, y, data)

    else:
        return

    fig.savefig(output_name)
    plt.close()

    return output_name


class Streamer(QThread):
    """
    Handles communication to and from the rover platform (via a COM Port). Includes functions to send outgoing messages
    and parse incoming messages
    """
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = 'COM7'

    def __init__(self):
        super(Streamer, self).__init__()

    def changePort(self, port):
        """
        Changes the serial port to that specified
        :param port:
        :return:
        """
        self.ser.port = port

    def sendCommand(self, text):
        """
        Simply writes a text command over the serial port to a Rover Class Item
        :param text: Command (as bytearray)
        :return:
        """

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

    def portScan(self):

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

    def parseResponse(self, text):
        """
        Parses an incoming text string for data from the windrunner rover.
        :param text: Response (as bytearray)
        :return:
        """
        if text[0] == 36:  # If '$' is received
            if text[1] == 48:  # If CMD == 0
                self.updateDriveStatus(text[3])
            elif text[1] == 49:  # If CMD == 1
                lat = 0
                lon = 0
                for i in range(3, 6):
                    lat = (lat * 256) + text[i]
                for i in range(7, 10):
                    lon = (lon * 256) + text[i]
                self.updatePositionStatus([lat, lon])
            elif text[1] == 50:  # If CMD == 2
                x = text[3] * 256 + text[4]
                self.updateOrientationStatus(x / 100.0)
            elif text[1] == 51:  # If CMD == 3
                wind = (int(text[3]) / 256) * 32.4
                light = (int(text[4]) / 256) * 6000
                temp = (int(text[5]) / 256) * 100
                self.updateSensorStatus([wind, light, temp])
        else:
            print(text)

    def updateDriveStatus(self, code):
        """
        Updates the current drive status
        :param code: Data
        :return:
        """
        if code == 1:
            print("Drive Error Occurred")

    def updatePositionStatus(self, vals):
        """
        Updates the latitude/longitude sensor data arrays
        :param vals: Latitude/Longitude values
        :return:
        """
        latitude.append(vals[0])
        longitude.append(vals[1])

        return

    def updateOrientationStatus(self, val):
        """
        Updates the orientation sensor data array
        :param val: Orientation value
        :return:
        """
        ori = (-val + 360) + 83
        if ori > 360:
            ori = ori - 360

        orientation.append(ori)

        return

    def updateSensorStatus(self, vals):
        """
        Updates the wind speed, light intensity, and temperature data arrays
        :param vals: Wind Speed/Light Intensity/Temperature values
        :return:
        """
        wind_speed.append(vals[0])
        light_intensity.append(vals[1])
        temperature.append(vals[2])

        return

    def run(self):
        """
        Listens to serial port for incoming communicaiton from rover platform
        :return:
        """
        try:
            self.ser.open()
        except:
            print("Port Unavailable!")

        while True:
            if self.ser.in_waiting:
                self.ser.flush()
                msg = bytearray(self.ser.readline())
                self.parseResponse(msg)
        self.ser.close()


class Server(QThread):
    """
    Handles the running of the local web server application
    """

    # Signal to communicate rover commands from the web server to the main Qt application
    newcommand = pyqtSignal(str, list)

    def __init__(self, dataHandler):
        """
        Initializes the web server application
        :param dataHandler: Data handler to send rover commands via the Streamer
        """
        super(Server, self).__init__()
        self.newcommand.connect(dataHandler)
        self.collection_mode: str = ""

    def run(self):
        """
        Runs the web server
        :return:
        """
        app = Flask(__name__)

        @app.route("/", methods=["POST", "GET"])
        def display_page():
            if request.method == 'POST':
                del latitude[:-1]
                del longitude[:-1]
                del orientation[:-1]
                del temperature[:-1]
                del light_intensity[:-1]
                del wind_speed[:-1]

            return render_template(
                "rover_control.html",
                latitude=latitude[-1],
                longitude=-longitude[-1],
                orientation=orientation[-1],
                temperature=temperature[-1],
                light_intensity=light_intensity[-1],
                wind_speed=wind_speed[-1]
            )

        @app.route("/collect_data", methods=["POST", "GET"])
        def collect_data():

            # Emit a signal from HTML form data
            if request.method == 'POST':
                form_data = request.form

                self.collection_mode = form_data["control_type"]

                if self.collection_mode == "autonomous":
                    global row_length
                    row_length = int(form_data["num_of_cols"])
                    global col_length
                    col_length = int(form_data["num_of_rows"])

                    self.newcommand.emit(
                        self.collection_mode,
                        [form_data["num_of_cols"], form_data["num_of_rows"]]
                    )
                elif self.collection_mode == "remote":
                    self.newcommand.emit(
                        self.collection_mode,
                        [form_data["direction"], form_data["duration"], form_data["speed"], form_data["num_points"]]
                    )

            # Clear old visualizations
            folder = './static/images'
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                os.remove(file_path)

            if self.collection_mode == "autonomous":
                return render_template(
                    "collect_data.html",
                    latitude=latitude[-1],
                    longitude=-longitude[-1],
                    orientation=orientation[-1],
                    temperature=temperature[-1],
                    temperature_img=generateVisualization(
                        temperature,
                        "Temperature",
                        "./static/images/",
                        "3D"),
                    light_intensity=light_intensity[-1],
                    light_intensity_img=generateVisualization(
                        light_intensity,
                        "Light Intensity",
                        "./static/images/",
                        "3D"),
                    wind_speed=wind_speed[-1],
                    wind_speed_img=generateVisualization(
                        wind_speed,
                        "Wind Speed",
                        "./static/images/",
                        "3D")
                )
            elif self.collection_mode == "remote":
                return render_template(
                    "collect_data.html",
                    latitude=latitude[-1],
                    longitude=-longitude[-1],
                    orientation=orientation[-1],
                    temperature=temperature[-1],
                    temperature_img=generateVisualization(
                        temperature,
                        "Temperature",
                        "./static/images/",
                        "2D"),
                    light_intensity=light_intensity[-1],
                    light_intensity_img=generateVisualization(
                        light_intensity,
                        "Light Intensity",
                        "./static/images/",
                        "2D"),
                    wind_speed=wind_speed[-1],
                    wind_speed_img=generateVisualization(
                        wind_speed,
                        "Wind Speed",
                        "./static/images/",
                        "2D")

                )
            else:
                exit(1)

        # Wait for sensor data to be initialized
        while len(latitude) == 0 or len(longitude) == 0 or len(orientation) == 0 or len(temperature) == 0 or len(light_intensity) == 0 or len(wind_speed) == 0:
            continue

        app.run("0.0.0.0", "5010")


class Rover(QObject):
    """
    Rover constructor which allows the passing of handler functions for when the windrunner sends valid commands back
    """

    def __init__(self):
        super(Rover, self).__init__()
        pass

    def createSendDriveCmd(self, direction, duration, speed):

        """
        Function takes in below described arguments and returns a bytearray with the
        ASCII Data necessary to command the Windrunner Rover to complete the given
        command.

        :param direction: Direction for the rover platform to move (Forward, Backward, Left, Right)
        :param duration: Duration of rover platform movement
        :param speed: Speed of rover platform movement
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


