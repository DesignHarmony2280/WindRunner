#include <SoftwareSerial.h>

/**
    CLASS: Packet
    This class provides the functions for a packet either tx or
    rx via the radio module.
*/
class Packet {

  public:
    Packet(uint8_t id, uint8_t *data, uint8_t len) {
      this->id = id + 48;   // ascii offset
      this->len = len + 3;  // header offset
      this->data = data;
    }

    uint8_t id;
    uint8_t *data;
    uint8_t len;
};

class Timer {

  public:
    Timer() {
      duration = 0;
    }

    void start(uint32_t ms) {
      startTime = millis();
      duration = ms;
      isRun = true;
    }

    void stop() {
      isRun = false;
    }

    bool check() {
      currentTime = millis();
      if (currentTime >= startTime + duration) {
        isRun = false;
        return (true);
      }
      else
        return (false);
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

void drive(way dir, uint8_t spd) {
  digitalWrite(4, (dir & 2) >> 1);
  analogWrite(5, spd);
  digitalWrite(7, dir & 1);
  analogWrite(6, spd);
}

float getTemp();
float getLight();
float getWind();

Timer* driveTimer   = new Timer();
Timer* msgTimer     = new Timer();

uint8_t data []     = {1};
uint8_t pos []      = {48, 48, 49, 49, 50, 50, 51, 51};
uint8_t compass []  = {48, 48, 49, 49, 50, 50};
uint8_t sense []    = {48, 48, 49};

Packet* driveStat   = new Packet (0, data,    sizeof(data));
Packet* posData;
Packet* compData;
Packet* senseData;

void setup() {
  Serial.begin(9600);

  pinMode(13, OUTPUT);
}

void loop() {

  // put your main code here, to run repeatedly:
  //Serial.println((analogRead(A1)/255.0)*100);

  //txPacket(compData);

  if (Serial.available())
    rxPacket();

  if (driveTimer->isRun && driveTimer->check()) {
    drive(BKW, 0); // stop driving
    data[0] = 1;
    txPacket(driveStat);
  }

  delay(100);
}

void txPacket (Packet *msg) {
  Serial.write('$');
  Serial.write(msg->id);
  Serial.write(msg->len);
  for (uint8_t i = 0; i < msg->len - 3; i++) {
    Serial.write(msg->data[i]);
  }
  Serial.println(); // crucial for python GUI readline
}

bool rxPacket() {
  if (Serial.read() == '$') {
    while (!Serial.available());
    uint8_t id = Serial.read();
    while (!Serial.available());
    uint8_t len = Serial.read() - 48; //remove mask when actual sending implemented

    if (id == 48) {
      while (!Serial.available());
      uint8_t dir = Serial.read() - 48; //remove mask when actual sending implemented
      while (!Serial.available());
      uint8_t spd = Serial.read();
      len = len - 5;
      uint32_t dur = 0;

      for (len; len > 0; len--) {
        while (!Serial.available());
        dur = (dur * 256) + Serial.read();
      }

      drive(dir, spd);
      driveTimer->start(dur);
    } else if (id == 49) {
      posData = new Packet (1, pos, sizeof(pos));
      txPacket(posData);
    } else if (id == 50) {
      compData = new Packet (2, compass, sizeof(compass));
      txPacket(compData);
    } else if (id == 51) { // Sensor Command
      sense[0] = analogRead(A2);  // read Wind
      sense[1] = analogRead(A0);  // read Light
      sense[2] = analogRead(A1);  // read Temperature
      senseData = new Packet (3, sense, sizeof(sense));
      txPacket(senseData);
    } else {
      Serial.println(id);
    }
  } else {
    return (false);
  }
}
