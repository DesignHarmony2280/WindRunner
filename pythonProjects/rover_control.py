from PyQt5 import QtWidgets
import sys
import time
import utilities as ut
import typing


class RoverControl(QtWidgets.QMainWindow):
    """
    Handles the control of the rover platform
    """
    def __init__(self):
        super(RoverControl, self).__init__()

        # Instantiates the rover class
        self.rover = ut.Rover()

        # Sets up the serial port stream
        self.stream = ut.Streamer()

        # Populates the COM Port list with the available COM ports
        self.comPorts = self.stream.portScan()

        # Sets COM Port
        self.stream.changePort(str(self.comPorts[0]))

        # Starts the Streamer Qthread
        try:
            self.stream.start()
        except:
            exit(1)

        # Need to wait for the streamer class to be initialized
        # FIXME: Determine source of timing issue
        time.sleep(2)

        # Initialize Sensor Data
        self.stream.sendCommand(self.rover.createSendPosCmd())
        self.stream.sendCommand(self.rover.createSendSenseCmd())
        # self.stream.sendCommand(self.rover.createSendOriCmd())

        # Initialize and start web server
        self.server = ut.Server(dataHandler=self.sendServerCommand)
        self.server.start()

        return

    def sendServerCommand(self, command: str, vals: typing.List):
        """
        Data handler for sending rover commands from the web server
        :param command: Operation mode of the rover (autonomous or remote)
        :param vals: List of values for each operation mode
        :return:
        """
        if command == "autonomous":
            self.grid(
                int(vals[0]),
                int(vals[1]),
            )
        elif command == "remote":
            self.single_path(
                vals[0],
                int(vals[1]),
                int(vals[2]),
                int(vals[3]),
            )

        return

    def single_path(self, direction: str, duration: int, speed: int, num_point: int):
        """
        Collects sensor on a straight path via rover commands
        :param direction: Direction for the rover platform to move (Forward, Backward, Left, Right)
        :param duration: Duration of rover platform movement
        :param speed: Speed of rover platform movement
        :param num_point: Number of sensor data points to collect
        :return:
        """

        for i in range(num_point):
            # Send drive command to rover
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction=direction,
                    duration=duration,
                    speed=speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(duration)

            # Collect sensor data for point
            self.stream.sendCommand(self.rover.createSendPosCmd())
            self.stream.sendCommand(self.rover.createSendSenseCmd())
            # self.stream.sendCommand(self.rover.createSendOriCmd())

        return

    # FIXME: Set the duration and speed values for turning and moving forward
    def grid(self, num_of_cols: int, num_of_rows):
        """
        Based on an input number of rows and columns, collects a sensor data within a grid
        :param num_of_cols: Number of rows within the collection grid
        :param num_of_rows: Number of columns within the collection grid
        :return:
        """
        moving_duration: int = 3
        moving_speed: int = 3

        turning_duration: int = 1
        turning_speed: int = 1

        i: int = num_of_cols
        while True:
            for j in range(num_of_rows -  1):
                self.stream.sendCommand(
                    self.rover.createSendDriveCmd(
                        direction="forward",
                        duration=moving_duration,
                        speed=moving_speed
                    )
                )

                # Wait for rover to stop moving
                time.sleep(moving_duration)

                self.stream.sendCommand(self.rover.createSendSenseCmd())
                self.stream.sendCommand(self.rover.createSendPosCmd())
                # self.stream.sendCommand(self.rover.createSendOriCmd())

            i -= 1
            if i == 0:
                break

            # Turn right
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction="right",
                    duration=turning_duration,
                    speed=turning_speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(turning_duration)

            # Move forward
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction="forward",
                    duration=moving_duration,
                    speed=moving_speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(moving_duration)

            self.stream.sendCommand(self.rover.createSendSenseCmd())
            self.stream.sendCommand(self.rover.createSendPosCmd())
            # self.stream.sendCommand(self.rover.createSendOriCmd())

            # Turn right
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction="right",
                    duration=turning_duration,
                    speed=turning_speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(turning_duration)

            for j in range(num_of_rows -  1):
                self.stream.sendCommand(
                    self.rover.createSendDriveCmd(
                        direction="forward",
                        duration=moving_duration,
                        speed=moving_speed
                    )
                )

                # Wait for rover to stop moving
                time.sleep(moving_duration)

                self.stream.sendCommand(self.rover.createSendSenseCmd())
                self.stream.sendCommand(self.rover.createSendPosCmd())
                # self.stream.sendCommand(self.rover.createSendOriCmd())

            i -= 1
            if i == 0:
                break

            # Turn left
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction="left",
                    duration=turning_duration,
                    speed=turning_speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(turning_duration)

            # Move forward
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction="forward",
                    duration=moving_duration,
                    speed=moving_speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(moving_duration)

            self.stream.sendCommand(self.rover.createSendSenseCmd())
            self.stream.sendCommand(self.rover.createSendPosCmd())
            # self.stream.sendCommand(self.rover.createSendOriCmd())

            # Turn left
            self.stream.sendCommand(
                self.rover.createSendDriveCmd(
                    direction="left",
                    duration=turning_duration,
                    speed=turning_speed
                )
            )

            # Wait for rover to stop moving
            time.sleep(turning_duration)

        return


if __name__ == "__main__":
    # Instantiate rover
    app = QtWidgets.QApplication(sys.argv)
    rover_control = RoverControl()
    app.exec_()


