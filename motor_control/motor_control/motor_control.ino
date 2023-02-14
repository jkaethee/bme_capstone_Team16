#include <SoftwareSerial.h>

// Bluetooth connection
SoftwareSerial mySerial(3,2);

// Motor A connections - right motor
int enA = 9;
int in1 = 8;
int in2 = 7;

// Motor B connections - left motor
int enB = 3;
int in3 = 5;
int in4 = 4;

// Motor default speed
int speed = 200; 

void setup() {
  // Open Bluetooth serial port
  mySerial.begin(9600); 

	// Set all the motor control pins to outputs
	pinMode(enA, OUTPUT);
	pinMode(enB, OUTPUT);
	pinMode(in1, OUTPUT);
	pinMode(in2, OUTPUT);
	pinMode(in3, OUTPUT);
	pinMode(in4, OUTPUT);
	
	// Turn off motors - initial state
	digitalWrite(in1, LOW);
	digitalWrite(in2, LOW);
	digitalWrite(in3, LOW);
	digitalWrite(in4, LOW);
}

void loop() {
  // Do nothing until Bluetooth received command
  while(!mySerial.available());

  // Received forward command 
  if (mySerial.readString()) == "1") {
    move_forward();
  } 
  
  // Received left turn command 
  else if (mySerial.readString()) == "2") {
    rotate_left(175);
  } 

  // Received right turn command 
  else if (mySerial.readString()) == "3") {
    rotate_right(175);
  } 

  // Received stop command 
  else if (mySerial.readString()) == "4") {
    brake();
  } 

  // Received invalid command - do nothing
  else {
    brake();
  }
}

// How fast do we want to turn? If base speed, won't we turn too quickly?
void rotate_left(int turn_speed) {
  analogWrite(enA, turn_speed);
	analogWrite(enB, turn_speed);

	// Reverse motor A and forward motor B 
	digitalWrite(in1, LOW);
	digitalWrite(in2, HIGH);
	digitalWrite(in3, HIGH);
	digitalWrite(in4, LOW);
}

void rotate_right(int turn_speed) {
  analogWrite(enA, turn_speed);
	analogWrite(enB, turn_speed);

	// Reverse motor B and forward motor A 
	digitalWrite(in1, HIGH);
	digitalWrite(in2, LOW);
	digitalWrite(in3, LOW);
	digitalWrite(in4, HIGH);
}

// Do we want to slowly brake or just do a full stop?
void brake() {

  for (int i = speed; i >= 0; --i) {
		analogWrite(enA, i);
		analogWrite(enB, i);
		delay(20);
	}
	
	// Now turn off motors
	digitalWrite(in1, LOW);
	digitalWrite(in2, LOW);
	digitalWrite(in3, LOW);
	digitalWrite(in4, LOW);
  
}

void move_forward() {
  // Set motors to maximum speed
	// For PWM maximum possible values are 0 to speed value
  analogWrite(enA, speed);
	analogWrite(enB, speed);


  // Turn on motor A & B
	digitalWrite(in1, HIGH);
	digitalWrite(in2, LOW);
	digitalWrite(in3, HIGH);
	digitalWrite(in4, LOW);
}

