#include <Arduino.h>
#include <Servo.h>

#define fanpin 2
#define motorpin 11

int incomingByte = 0;
Servo s1;
Servo s2;
Servo s3;
Servo s4;

void ServoStart() {
  s1.write(0);
  s2.write(180);
  s3.write(180);
  s4.write(0);
}

void Dispense() {
  s1.write(180);
  s2.write(0);
  s3.write(0);
  s4.write(180);
  digitalWrite(motorpin, HIGH);
  delay(2000);
  digitalWrite(motorpin, LOW);
  delay(2000);
}

void ServoEnd() {
  digitalWrite(fanpin, HIGH);
  delay(4000);
  s1.write(180);
  s2.write(0);
  s3.write(0);
  s4.write(180);
  delay(4000);
  digitalWrite(fanpin, LOW);
}


void setup() {
  Serial.begin(115200);
  s1.attach(3);
  s2.attach(5);
  s3.attach(6);
  s4.attach(9);
  pinMode(fanpin, OUTPUT);
  pinMode(motorpin, OUTPUT);

  s1.write(180);
  s2.write(0);
  s3.write(0);
  s4.write(180);
  digitalWrite(fanpin, LOW);
  digitalWrite(motorpin, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte	== 101) {
      Serial.println("ight ending");
      ServoEnd();
    } else if (incomingByte == 115) {
      Serial.println("starting???");
      Dispense();
      ServoStart();
    } else {
      Serial.println("wrong");
    }
  }
}