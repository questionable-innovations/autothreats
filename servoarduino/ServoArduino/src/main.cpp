#include <Arduino.h>
#include <Servo.h>

Servo s1;
// Servo s2;
// Servo s3;
// Servo s4;

void ServoStart() {
  s1.write(0);
  delay(1000);
  // s2.write(180);
  // delay(1000);
  // s3.write(180);
  // delay(1000);
  // s4.write(0);
  // delay(1000);
}

void ServoEnd() {
  s1.write(180);
  delay(1000);
  // s2.write(0);
  // delay(1000);
  // s3.write(0);
  // delay(1000);
  // s4.write(180);
  // delay(1000);
}


void setup() {
  Serial.begin(9600);
  s1.attach(3);
  // s2.attach(5);
  // s3.attach(6);
  // s4.attach(9);
}

void loop() {
  ServoStart();
  // delay(3000);
  ServoEnd();
  // delay(1000);
}