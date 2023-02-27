#include <SoftwareSerial.h>
#include <string.h> 

// Bluetooth connection
SoftwareSerial BTSerial(13,12); //Tx, Rx

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

char c = ' ';

void setup() {
  // Open Bluetooth serial port
  BTSerial.begin(38400); 
  Serial.begin(9600);
  BTSerial.setTimeout(1);


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
  if (BTSerial.available()){
    char temp = BTSerial.read(); // send from serial to bluetooth
    if ((temp == '1') ||  (temp == '2') || (temp == '3') ||  (temp == '4') ||  (temp == 'q')){
      c = temp;
      Serial.print("string: ");
      Serial.println(c);

    }
  }

  // Received forward command 
  if (c == '1') {
    Serial.println("Going forward!");
    move_forward();
  } 
  
  // Received left turn command 
  else if (c == '2') {
    Serial.println("Turn left!");
    rotate_left(175);
  } 

  // Received right turn command 
  else if (c == '3') {
    Serial.println("Turn right!");
    rotate_right(175);
  } 

  // Received stop command 
  else if (c == '4') {
    Serial.println("Stop!");
    brake();
  } 

  // Received invalid command - do nothing
  else {
    brake();
  }
}

void rotate_right(int turn_speed) {
  analogWrite(enA, turn_speed);
	analogWrite(enB, turn_speed);

	// Reverse motor A and forward motor B 
	digitalWrite(in1, LOW);
	digitalWrite(in2, HIGH);
	digitalWrite(in3, HIGH);
	digitalWrite(in4, LOW);
}

void rotate_left(int turn_speed) {
  analogWrite(enA, turn_speed);
	analogWrite(enB, turn_speed);

	// Reverse motor B and forward motor A 
	digitalWrite(in1, HIGH);
	digitalWrite(in2, LOW);
	digitalWrite(in3, LOW);
	digitalWrite(in4, HIGH);
}

void brake() {
	
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
	digitalWrite(in1, LOW);
	digitalWrite(in2, HIGH);
	digitalWrite(in3, LOW);
	digitalWrite(in4, HIGH);
}

