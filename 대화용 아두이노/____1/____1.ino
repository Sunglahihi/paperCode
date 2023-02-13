#include <Servo.h>

Servo myservoH;
// 대화용, 박스에서 위, COM3

int posW = 1 0;
void setup() {
  myservoH.attach(9);
  Serial.begin(9600);
}


void loop() {
  myservoH.write(posW);
  while (Serial.available() > 0) {
    long value = Serial.parseInt();
    myservoH.write(value);
    Serial.println(value);
  }
  
}
