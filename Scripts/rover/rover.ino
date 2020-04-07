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

class Timer {

public:
  Timer(){
    duration = 0;
  }

  void start(uint32_t ms){
    startTime = millis();
    duration = ms;
    isRun = true;
  }

  void stop(){
    isRun = false;
  }

  bool check(){
    currentTime = millis();
    if (currentTime >= startTime + duration){
      isRun = false;
      return(true);
    }
    else
      return(false);
  }

  bool isRun;
  uint32_t startTime;
  uint64_t currentTime;
  uint32_t duration;
};

typedef enum {
  BKW,
  LFT,
  RGT,
  FWD
} way;

void txPacket (Packet msg);

void drive(way dir, uint8_t spd){
  digitalWrite(4, (dir & 2) >> 1);
  analogWrite(5, spd);
  digitalWrite(7, dir & 1);
  analogWrite(6, spd);
}

Timer* driveTimer = new Timer();
Timer* msgTimer = new Timer();

uint8_t data [] = {1};

Packet* driveStat = new Packet (0, data, sizeof(data));

void setup() {
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  //Serial.println((analogRead(A1)/255.0)*100);

  if(Serial.available())
    rxPacket();

  if (driveTimer->isRun && driveTimer->check()){
    drive(BKW, 0); // stop driving
    txPacket(driveStat);
  }
}

void txPacket (Packet *msg) {
  Serial.print('$');
  Serial.print(msg->id);
  Serial.print(msg->len);
  for (uint8_t i = 0; i < msg->len - 3; i++){
    Serial.print(msg->data[i]);
  }
}

bool rxPacket() {
  if(Serial.read() == '$'){
    while(!Serial.available());
    uint8_t id = Serial.read();
    while(!Serial.available());
    uint8_t len = Serial.read() - 48; //remove mask when actual sending implemented
    
    switch(id){
      case '0':
        while(!Serial.available());
        uint8_t dir = Serial.read() - 48; //remove mask when actual sending implemented
        while(!Serial.available());
        uint8_t spd = Serial.read();
        len = len - 5;
        uint32_t dur = 0;

        for (len; len > 0; len--){
          while(!Serial.available());
          dur = (dur * 256) + Serial.read();
        }

        drive(dir, spd);
        driveTimer->start(dur);
        break;
      default:
        break;
    }
  } else {
    return(false);
  }
}
