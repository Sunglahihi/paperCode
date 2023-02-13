#include <Servo.h>

Servo myservoW;  // create servo object to control a servo

// 추적용, 박스에서 밑, COM4

int posW = 10;
long value;

void setup() {
  myservoW.attach(10);
  Serial.begin(9600);
}

void loop() {
  value = Serial.parseInt();
  delay(1500); //0.5초마다 옆으로 돔, 총 8초
  posW = posW + 10;
  if (value == 1) {
    Serial.println(posW);
    value = 0;
  }
  if (posW < 10 || posW > 170) {
    posW = 10;
  }
  myservoW.write(posW);
  delay(1000);
}
