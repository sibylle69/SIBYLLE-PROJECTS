#include <SPI.h>        //SPI library for communicate with the nRF24L01+
#include "RF24.h"       //The main library of the nRF24L01+
#include <nRF24L01.h>   
#include <LiquidCrystal.h>  //LCD display

//variables definition
int msg[1];
int N;
int R;
int state = 0;
int var = 0;
int previous_N;
int previous_R;
int new_value_sent;
int sum = 0;
int total = 0;

//LCD display
int Contrast=100;
LiquidCrystal lcd(7, 8, 5, 4, 3, 2);  

int buttonValue; //Stores analog value when button is pressed
const int button = 1;

//define the flex sensor input pins
int flex_3 = A3;
int flex_2 = A2;
int flex_1 = A1;

//define variables for flex sensor values
int flex_3_val;
int flex_2_val;
int flex_1_val;

//Define object from RF24 library - 9 and 10 are a digital pin numbers to which signals CE and CSN are connected.
RF24 radio(9,10);

//Create a pipe addresses for the communicate                                    
const uint64_t pipe = 0xE8E8F0F0E1LL;

int request() {
    R = random(1, 4);
    R -= 1;
    lcd.clear();
    lcd.setCursor(2, 0);
    lcd.print("Give me ");
    lcd.setCursor(11, 0);
    lcd.print(R);
    previous_R = R;
}

int check() {
  sum = N + previous_N;
  total += N;
    
  if (N == R){   //if right answer
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Well done!");
    lcd.setCursor(0, 1);
    lcd.print(N); lcd.print("+"); lcd.print(previous_N); 
    lcd.print("="); lcd.print(sum);
    lcd.print(" TOTAL = "); lcd.print(total);
  }

   else{
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("That was "); lcd.print(N); lcd.print(",not "); lcd.print(R);
      lcd.setCursor(0, 1);
      lcd.print(N); lcd.print("+"); lcd.print(previous_N); 
      lcd.print("="); lcd.print(sum);
      lcd.print(" TOTAL = "); lcd.print(total);
   }
}

void setup(void){
  Serial.begin(9600);
  radio.begin();                 //Start the nRF24 communicate     
  radio.openWritingPipe(pipe);   //Sets the address of the receiver to which the program will send data.
  radio.setPALevel(RF24_PA_MIN);
  radio.stopListening();

  pinMode(flex_3, INPUT);
  pinMode(flex_2, INPUT);
  pinMode(flex_1, INPUT);
  pinMode(button, OUTPUT);
  
  analogWrite(6,Contrast);
  lcd.begin(16, 2);
}

void loop(void){

    buttonValue = analogRead(A6); //Read analog value from A0 pin
    
  // START INTRO
  if (state == 0){
    lcd.clear(); 
    lcd.setCursor(0, 0);
    lcd.print("Welcome!");
    lcd.setCursor(0, 1);
    lcd.print("ready to learn?");

    if (buttonValue <= 150){  //if pressed
      state = 1;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Use your fingers");
      lcd.setCursor(0, 1);
      lcd.print("for additions :)");
      
      delay(2000);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("LET'S GO !");
      delay(2000);
      request();     
      }
  }
  delay(100);

  //read the sensor values
  flex_3_val = analogRead(flex_3);
  flex_2_val = analogRead(flex_2);
  flex_1_val = analogRead(flex_1);
  Serial.println(flex_3_val);

  //check whether the fingers are bent
  if(flex_3_val < 500) {   //bent
    N += 1;
  }

  if(flex_2_val < 800) {   //bent
    N += 1;
  }

  if(flex_1_val < 800) {   //bent
    N += 1;
  }

  //identify a finger movement
  if (!(N == previous_N) && !(N == 0) && (state == 1)) {   //a change
    new_value_sent = N; //do something
    Serial.println(new_value_sent);
    check();
    previous_N = N;
    delay(7000);
    request();
  }

  //check if robot reached end of the playground
  if(total >= 6) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Game is over");
    lcd.setCursor(0, 1);
    lcd.print("Well done!");
    delay(10000);
  }

  //send data to robot
  msg[0] = N;
  radio.write(&msg, 1);
  delay(10);
  N = 0; 
}
