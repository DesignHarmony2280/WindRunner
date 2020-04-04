# ELE 408 - Windrunner Manual
## Timothy Boyd and Daniel Forman

### Commands -
For any command transfer between the rover and the controller, the message must begin with
the start '$' character.

The standard packet type is shown as follows:

| start | id | length | content n | ... | content 0 |

#### CMD ID '0' - Drive command
##### From GUI - 
| start | '0' | length | direction | speed MSB | ... | speed LSB |
##### From Rover
| start | '0' | length | status |

Here status will be either a 1 or 0, indicating whether or not the rover was able to fully
complete the drive command without being interrupted by some object.
