#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

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

void drive(way dir, uint8_t spd);

/* Assign a unique ID to this sensor at the same time */
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);

float getTemp();
float getLight();
float getWind();

Timer* driveTimer   = new Timer();
Timer* msgTimer     = new Timer();

uint8_t data []     = {0};
uint8_t pos []      = {48, 48, 49, 49, 50, 50, 51, 51};
uint8_t compass []  = {48, 48};
uint8_t sense []    = {48, 48, 49};

Packet* driveStat   = new Packet (0, data,    sizeof(data));
Packet* posData;
Packet* compData;
Packet* senseData;

void setup() {
  Serial.begin(9600);

  pinMode(13, OUTPUT);

    /* Initialise the sensor */
  if(!mag.begin())
  {
    /* There was a problem detecting the HMC5883 ... check your connections */
    Serial.println("Ooops, no HMC5883 detected ... Check your wiring!");
    while(1);
  }
}

void loop() {

  // put your main code here, to run repeatedly:
  //Serial.println((analogRead(A1)/255.0)*100);

  //txPacket(compData);

  if (Serial.available())
    rxPacket();

  if (driveTimer->isRun && driveTimer->check()) {
    drive(BKW, 0); // stop driving
    data[0] = 0;
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
      getOrientation();
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

void drive(way dir, uint8_t spd) {
  digitalWrite(4, (dir & 2) >> 1);
  analogWrite(5, spd);
  digitalWrite(7, dir & 1);
  analogWrite(6, spd);
}

float getOrientation (){
  /* Get a new sensor event */ 
  sensors_event_t event; 
  mag.getEvent(&event);
  
   // Hold the module so that Z is pointing 'up' and you can measure the heading with x&y
  // Calculate heading when the magnetometer is level, then correct for signs of axis.
  float heading = atan2(event.magnetic.y, event.magnetic.x);
  
  // Once you have your heading, you must then add your 'Declination Angle', which is the 'Error' of the magnetic field in your location.
  // Find yours here: http://www.magnetic-declination.com/
  // Mine is: -13* 2' W, which is ~13 Degrees, or (which we need) 0.22 radians
  // If you cannot find your Declination, comment out these two lines, your compass will be slightly off.
  float declinationAngle = 0.22;
  heading += declinationAngle;
  
  // Correct for when signs are reversed.
  if(heading < 0)
    heading += 2*PI;
    
  // Check for wrap due to addition of declination.
  if(heading > 2*PI)
    heading -= 2*PI;
   
  // Convert radians to degrees for readability.
  float headingDegrees = heading * 180/M_PI; 

  int deg = headingDegrees*100;
  compass[0] = (deg & 0xFF00) >> 8; // MSB
  compass[1] = (deg & 0x00FF);      // LSB
}
