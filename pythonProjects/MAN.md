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

| start | '1' | 

##### From Rover

| start | '1' | length | lat. MSB | ... | lat. LSB | lon. MSB | ... | lon. LSB | 

#### CMD ID '2' - 'Orientation Command'


#### CMD ID '3' - 'Sensor Data Command'

