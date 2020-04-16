# ELE 408 - Windrunner Manual
## Timothy Boyd and Daniel Forman

### Commands -
For any command transfer between the rover and the controller, the message must begin with
the start '$' character.

The standard packet type is shown as follows:

| start | id | length | content n | ... | content 0 |

#### CMD ID '0' - 'Drive Command'
##### From GUI - 
| start | '0' | length | direction | speed MSB | ... | speed LSB |
##### From Rover
| start | '0' | length | status |

Here status will be either a 1 or 0, indicating whether or not the rover was able to fully
complete the drive command without being interrupted by some object.

#### CMD ID '1' - 'Position Command'

Each Lattitude or Longitude data item can be represented as a 16-bit float variable. In order to cut
down on the number of packets sent, the controller must send an initiate read command, which will be
answered with a command containing each degree 

##### From GUI - 
Very simple, just a ping to the rover that the program would like the position of the rover.

| start | '1' | 

##### From Rover -

| start | '1' | length | lat. MSB | ... | lat. LSB | lon. MSB | ... | lon. LSB | 

#### CMD ID '2' - 'Orientation Command'

The HMC5883 I2C Compass sends 12bit data regarding x, y, and z coordinates of the rover in terms of its magnetometer.
Therefore data sent over the serial port will take the form of three 16 bit numbers.

##### From GUI -

Very simple, just a ping to the rover that the program would like the position of the rover.

| start | '2' | 

##### From Rover - 

| start | '2' | length | X MSB | X LSB | Z MSB | Z LSB | Y MSB | Y LSB |

#### CMD ID '3' - 'Sensor Data Command'

The wind speed, light intensity, and temperature data all consist of a single byte of information, therefore the 
sent and received data will be similar to the last two commands, having all three of the data points obtainable with
one command.

##### From GUI -

Very simple, just a ping to the rover that the program would like the position of the rover.

| start | '3' | 

##### From Rover - 

| start | '3' | length | Wind Speed | Light Intensity | Temperature |

The wind speed will be a scaled 8 bit number representing 0 - 32.4 m/s wind speed
The light intensity will be an 8 bit number representing 0 - 6000 Lux
The temperature data will be an 8 bit number representing 0 - 100 deg C
