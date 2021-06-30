
#include <SPI.h>      //SPI library for communicate with the nRF24L01+
#include "RF24.h"     //The main library of the nRF24L01+

//Define enable pins of the Motors
const int ENABLE = 3;
const byte redLED = 4;
const byte greenLED = 5;
int SPEAKER = A4;    // The speaker is on pin 8

//Define control pins of the Motors
//If the motors rotate in the opposite direction, you can change the positions of the following pin numbers
const int DIRA = 7;    // Motor (+)
const int DIRB = 6;    // Motor (-)

//variables definition
int msg[1];
int data;
int buzzer_state = 0;
int A = 0;
int B = 0;
int C = 0;

//Define object from RF24 library - 9 and 10 are a digital pin numbers to which signals CE and CSN are connected
RF24 radio(9,10);

//Create a pipe addresses for the communicate
const uint64_t pipe = 0xE8E8F0F0E1LL;

//function that makes the robot walk a specific number of steps
int step(int i) {
  //drive step(s)          
  analogWrite(ENABLE,255); //enable on at speed 255
  digitalWrite(DIRA,HIGH); //one way
  digitalWrite(DIRB,LOW);
  delay(i * 2200);
  analogWrite(ENABLE,0); //enable off
}

//functino that activates a buzzer sequence
int buzzer() {

  digitalWrite(redLED, HIGH);
  tone(SPEAKER, 30, 1500);
  delay(1000);
  digitalWrite(redLED, LOW);

  digitalWrite(redLED, HIGH);
  tone(SPEAKER, 30, 1500);
  delay(1000);
  digitalWrite(redLED, LOW);

  digitalWrite(redLED, HIGH);
  tone(SPEAKER, 30, 1500);
  delay(1000);
  digitalWrite(redLED, LOW);

  digitalWrite(greenLED, HIGH);
  tone(SPEAKER, 60, 1000);
  delay(1300);
}

void setup(){
  //Define the motor pins as OUTPUT
  pinMode(ENABLE,OUTPUT);
  pinMode(DIRA,OUTPUT);
  pinMode(DIRB,OUTPUT);
  pinMode(SPEAKER, OUTPUT);
  
  Serial.begin(9600);
  radio.begin();                    //Start the nRF24 communicate            
  radio.openReadingPipe(1, pipe);   //Sets the address of the transmitter to which the program will receive data.
  radio.startListening(); 
  }

void loop(){
  if (radio.available()){
    radio.read(&msg, 1);   //read the data from the glove
    data = msg[0];
    delay(1000);

    //walk 1 if 1 finger showed
    if ((A == 0) && (data == 1)){
      if (buzzer_state == 0) {
        buzzer();
        buzzer_state = 1;
      }
      digitalWrite(greenLED, HIGH);
      step(1);
      digitalWrite(greenLED, LOW);
      A = 1;
      B = 0;
      C = 0;
    }

    //walk 2 if 2 fingers showed
    else if((B == 0) && (data == 2)){
      if (buzzer_state == 0) {
        buzzer();
        buzzer_state = 1;
      }      
      digitalWrite(greenLED, HIGH);
      step(2);
      digitalWrite(greenLED, LOW);
      B = 1;
      A = 0;
      C = 0;
    }

    //walk 3 if 3 fingers showed
    else if (C == 0 && data == 3){
      if (buzzer_state == 0) {
        buzzer();
        buzzer_state = 1;
      }
      digitalWrite(greenLED, HIGH);
      step(3);
      digitalWrite(greenLED, LOW);
      C = 1;
      A = 0;
      B = 0;
    }
  }
}
