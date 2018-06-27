#include <EEPROM.h> //include EEPROM library for saving state

//Configuration Variables:
#define FAN1_EEPROM_ADDR 0x01
#define FAN2_EEPROM_ADDR 0x02

//Pin Definitions:
//Big Easy Driver (Stepper Motor Controller)
#define STP 5 //BED will step the motor when it recieves a pulse on STP
#define DIR 6 //LOW is CCW, HIGH is CW
#define MS1 2 //MS1-MS3 set the microstep configuration of the BED
#define MS2 3
#define MS3 4

//L298 Motor Controller (Fan Controller)
#define FAN1 9  //tied to the EN pins of each channel on the L298
#define FAN2 10

//Filament Diameter Sensor
#define SENSOR A0 //analog pin the sensor output is attached to

//State Variables:
byte FAN1_STATE = 0;
byte FAN2_STATE = 0;
unsigned int SENSOR_STATE = 0;
signed long MOTOR_POSITION = 0;

void resetBEDPins() {
  digitalWrite(STP, LOW);
  digitalWrite(DIR, LOW);
  digitalWrite(MS1, LOW);
  digitalWrite(MS2, LOW);
  digitalWrite(MS3, LOW);//resets BED to default state with no microstepping
}

void singleStep(bool direction) {
  bool direction_prior_state = digitalRead(DIR); //save current directions setting to reset to at end of step
  digitalWrite(DIR, direction); //set the direction
  digitalWrite(STP, HIGH); //send a single pulse to step the motor
  delay(1);
  digitalWrite(STP, LOW);
  delay(1);
  digitalWrite(DIR, direction_prior_state); //reset DIR to its prior state//takes a single step in the direction specified
  if (direction) {
    MOTOR_POSITION++;
  }
  if (!direction) {
    MOTOR_POSITION--;
  }
}

void multiStep (unsigned int steps, bool direction) {
  for (unsigned int i = 0; i <= steps; i++) {
    singleStep(direction);
  }
}

void checkSerialInput() {
  if (Serial.available() == 1) {
    if (Serial.read() == 10) {
      Serial.println(SENSOR_STATE);
    }
  } else if (Serial.available() > 1) {
    String input = Serial.readString();
    input.toLowerCase();
    char fanType = input[1];
    if (input[0] == 'f' && (fanType == '1' || fanType == '2') && input[2] == ':') {
      String magnitudeString = input.substring(3);
      byte magnitude = magnitudeString.toInt();
      if (fanType == '1') {
        FAN1_STATE = magnitude;
      }
      if (fanType == '2') {
        FAN2_STATE = magnitude;
      }
      Serial.println("[Setting Fan " + String(fanType) + " to " + magnitude + "]");
    } else if (input[0] == 's' && (input[1] == 'f' || input[1] == 'r') && input[2] == ':') {
      String stepString = input.substring(3);
      unsigned int steps = stepString.toInt();
      if (input[1] == 'f') {
        multiStep(steps, true);
      }
      if (input[1] == 'r') {
        multiStep(steps, false);
      }
      Serial.println("[Moving motor " + String(steps) + " steps]");
    } else {
      Serial.println("Incorrect statement");
    }
  }
}


void retrieveFanState() { //retrieve last fan state from EEPROM and update state variables
  FAN1_STATE = EEPROM.read(FAN1_EEPROM_ADDR);
  FAN2_STATE = EEPROM.read(FAN2_EEPROM_ADDR);
}

void saveFanState() { //write current fan state to memory (only pushes if it's changed)
  //
  if ( EEPROM.read(FAN1_EEPROM_ADDR) != FAN1_STATE ) {
    EEPROM.write(FAN1_EEPROM_ADDR, FAN1_STATE);
  }
  if ( EEPROM.read(FAN2_EEPROM_ADDR) != FAN2_STATE ) {
    EEPROM.write(FAN2_EEPROM_ADDR, FAN2_STATE);
  }
}



void setup() {
  //initialize pins
  pinMode(STP, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(MS3, OUTPUT);
  pinMode(FAN1, OUTPUT);
  pinMode(FAN2, OUTPUT);
  pinMode(SENSOR, INPUT);

  //initialize serial
  Serial.begin(115200);

  //reset state to defaults
  resetBEDPins();
  analogWrite(FAN1, 0); //turn FAN1 off
  analogWrite(FAN2, 0); //turn FAN2 off

  //grab previous fan state from EEPROM
  retrieveFanState();

  //bring fans up to previous setting
  analogWrite(FAN1, FAN1_STATE);
  analogWrite(FAN2, FAN2_STATE);
}

void loop() {
  checkSerialInput();
  saveFanState();

  analogWrite(FAN1, FAN1_STATE);
  analogWrite(FAN2, FAN2_STATE);
  SENSOR_STATE = analogRead(SENSOR);

  //check serial to see if any new fan values have come
  //write them and update if they have
  //send current fan state and sensor value over serial
  delay(1);
}

