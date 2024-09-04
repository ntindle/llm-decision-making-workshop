#include <ArduinoBLE.h>
#include "ArduinoGraphics.h"
#include "Arduino_LED_Matrix.h"

#define DEBUG_MATRIX

#define PAIR_INTERVAL 30000   // interval for pairing in ms
#define CHARACTERISTIC_ID "19B10011-E8F2-537E-4F6C-D104768A1214"
#define BAUD_RATE 115200
#define ARDUINO_NAME "Arduino_Robotics"
#define TEAM_NO   23
#define SERVICE_ID "1ae49b08-b750-4ef7-afd8-5395763c0da6"

// Motor A connections
int enA = 13;  // 9
int in1 = 12;  // 8
int in2 = 11;  // 7
// Motor B connections
int enB = 8;   // 3
int in3 = 9;   // 5
int in4 = 10;  // 4

// Motor C connections
int enC = 7;
int in5 = 5;
int in6 = 6;

// Motor D connections
int enD = 2;
int in7 = 3;
int in8 = 4;


void bluetoothInit(ArduinoLEDMatrix &matrix, BLEService &controlService, BLEUnsignedIntCharacteristic &controlCharacteristic);
void startPairing();
void stopPairing();
bool isPairing();
void moveBot(String cmd);
void motorSetUp();

ArduinoLEDMatrix matrix;
BLEService controlService(SERVICE_ID);
BLEStringCharacteristic controlCharacteristic(CHARACTERISTIC_ID, BLERead | BLEWrite,512);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(BAUD_RATE);
  while (!Serial);
  //start LED matrix
  matrix.begin();
  matrix.stroke(0xFFFFFFFF);
  matrix.textScrollSpeed(40);
  matrix.textFont(Font_5x7);

  #ifdef DEBUG_MATRIX
    matrix.beginText(0, 1, 0xFFFFFF);
    matrix.println("   Starting BLE module   ");
    matrix.endText(SCROLL_LEFT);
  #endif
  
  bluetoothInit(matrix, controlService, controlCharacteristic);
  startPairing();
  matrix.println(TEAM_NO);
  matrix.endText();
}
bool moving = false;
unsigned long endMove = 0;
void loop() {
  // put your main code here, to run repeatedly:
  BLEDevice central = BLE.central();
  if(isPairing()){
    if(central.connected()){
      stopPairing();
    } else{
      // return;
    }
  } else if(!central.connected()){
    startPairing();
    return;
  }

  if(moving) {
    if(millis() >= endMove){
      Serial.println("stopping");
      stop_all_wheels();
      moving =  false;
    }
    return; // remove if you want to stop the bot while it's moving
  }

  // if(Serial.available()){
  //   Serial.read();
  //   char buffer[50];
  //   sprintf(buffer, "Current value: %u", controlCharacteristic.value());
  //   Serial.println(buffer);
  // }
  if(controlCharacteristic.written()){
    String val = controlCharacteristic.value();
    Serial.println(val);
    moveBot(val);
  }
}


void moveBot(String cmd){
  int index = cmd.indexOf('-');
  String dir = cmd.substring(0, index);
  String val = cmd.substring(index+1);
  Serial.println(val);
  Serial.println(dir);
  if(val.equals("short")){
    endMove = millis()+1000;
  } else if(val.equals("medium")){
    endMove = millis()+2000;
  } else if(val.equals("long")){
    endMove = millis()+3000;
  }
  if(dir.equals("left")){
    Serial.println("turn left");
    left_wheels_backwards();
    right_wheels_forwards();
  } else if(dir.equals("right")){
    Serial.println("turn right");
    right_wheels_backwards();
    left_wheels_forwards();
  } else if(dir.equals("forward")){
    Serial.println("move forward");
    left_wheels_forwards();
    right_wheels_forwards();
  } else /**if (dir.equals("backward"))**/{
    Serial.println("move backward");
    left_wheels_backwards();
    right_wheels_backwards();
  }
  moving = true;
}

// function defs, can ignore
const uint32_t anim_x[3] = {
		0x60670e39,
		0xc1f81f83,
		0x9c70e606
};
void bluetoothInit(ArduinoLEDMatrix &matrix, BLEService &controlService, BLEStringCharacteristic &controlCharacteristic){
  Serial.println("Starting BLE module");
   
  // begin bluetooth module initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE module failed!");

    #ifdef DEBUG_MATRIX
    matrix.println("   Failed to start BLE   ");
    matrix.endText(SCROLL_LEFT);
    #endif
    matrix.loadFrame(anim_x);
    while (1);
  }

  // set the local name peripheral advertises
  BLE.setLocalName(ARDUINO_NAME);
  // set the UUID for the service this peripheral advertises:
  BLE.setAdvertisedService(controlService);

  // add the characteristics to the service
  controlService.addCharacteristic(controlCharacteristic);

  // add the service
  BLE.addService(controlService);

  // start advertising
  BLE.advertise();

  Serial.println("Bluetooth® device active, waiting for connections...");

  #ifdef DEBUG_MATRIX
    matrix.println("   Bluetooth active.   ");
    matrix.endText(SCROLL_LEFT);
  #endif
}

void startPairing(){
  // startTime = millis();
  BLE.setPairable(Pairable::ONCE);
  Serial.println("pairing stated");
}
void stopPairing(){
  BLE.setPairable(false);
  Serial.println("pairing stopped");
}
bool isPairing(){
  return BLE.pairable();
}

void motorSetUp() {
  pinMode(enA, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(enC, OUTPUT);
  pinMode(enD, OUTPUT);

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(in5, OUTPUT);
  pinMode(in6, OUTPUT);

  pinMode(in7, OUTPUT);
  pinMode(in8, OUTPUT);

  // Turn off motors - Initial state
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  digitalWrite(in5, LOW);
  digitalWrite(in6, LOW);
  digitalWrite(in7, LOW);
  digitalWrite(in8, LOW);

  // set all motors to run at maximum speed, when spinning
  analogWrite(enA, 255);
  analogWrite(enB, 255);
  analogWrite(enC, 255);
  analogWrite(enD, 255);

  Serial.println("Motors have been initialised");
}


void left_wheels_forwards() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);

  digitalWrite(in5, LOW);
  digitalWrite(in6, HIGH);
}
void right_wheels_forwards() {
  digitalWrite(in7, LOW);
  digitalWrite(in8, HIGH);

  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
}
void left_wheels_backwards() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in5, HIGH);
  digitalWrite(in6, LOW);
}
void right_wheels_backwards() {
  digitalWrite(in7, HIGH);
  digitalWrite(in8, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
}
void stop_left_wheels() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in5, LOW);
  digitalWrite(in6, LOW);
}

void stop_right_wheels() {
  digitalWrite(in7, LOW);
  digitalWrite(in8, LOW);

  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}
void stop_all_wheels() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  digitalWrite(in5, LOW);
  digitalWrite(in6, LOW);
  digitalWrite(in8, LOW);
  digitalWrite(in7, LOW);
}