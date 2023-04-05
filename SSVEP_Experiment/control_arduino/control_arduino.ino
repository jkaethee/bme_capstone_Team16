int x;
int led1 = 9; 
int led2 = 10; 
int led3 = 11; 
int led4 = 12; 

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT);
  turn_everything_off(); 
}

void turn_everything_off() {

  for (int i=led1; i<=led4; i+=1){
      digitalWrite(i, LOW);
    }

}


void loop() {
  while (!Serial.available());

  turn_everything_off(); 
  
  x = Serial.readString().toInt();
  Serial.end();




  // digitalWrite(9,HIGH);

  // TODO: add cases to light up specific LEDs 
  // when reading a prediction

  // Forward
  if (x == 1){
    Serial.print("Received forward command");
    digitalWrite(led1, HIGH);
  }

  // Stop
  else if (x == 2){
    Serial.print("Received stop command");
    digitalWrite(led2, HIGH);
  }
  
  // Turn left
  else if (x == 3){
    Serial.print("Received turn left command");
    digitalWrite(led3, HIGH);
  }

  // Turn right
  else if (x == 4){
    Serial.print("Received turn right command");
    digitalWrite(led4, HIGH);
  }

  else{
    turn_everything_off(); 
    Serial.print("Invalid command");
  }

  // Serial.flush();
  Serial.begin(115200);


}