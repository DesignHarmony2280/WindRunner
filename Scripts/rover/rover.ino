#include <SoftwareSerial.h>

/**
*   CLASS: Packet
*   This class provides the functions for a packet either tx or
*   rx via the radio module.
*/
class Packet {

public:
  Packet(uint8_t id, uint8_t *data, uint8_t len) {
    this->id = id;
    this->len = len + 3;
    this->data = data;
  }

  uint8_t id;
  uint8_t *data;
  uint8_t len;
};

void txPacket (Packet msg);

SoftwareSerial funk (11, 10);

uint8_t data [] = {1, 2, 3, 4};

void setup() {
  Serial.begin(19200);
  Serial.println("Rover Begin");

  funk.begin(9600);

  Packet* msg = new Packet (1, data, sizeof(data));

  txPacket(msg);
}

void loop() {
  // put your main code here, to run repeatedly:

}

void txPacket (Packet *msg) {
  funk.print('$');
  funk.print(msg->id);
  funk.print(msg->len);
  for (uint8_t i = 0; i < msg->len - 3; i++){
    funk.print(msg->data[i]);
  }
}
