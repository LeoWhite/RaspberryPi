#include "IOpins.h"





// define global variables here
int  lowbat=550;                                       // default low battery voltage is 5.5V
int lmspeed,rmspeed;                                   // left and right motor speeds -255 to +255
boolean lmbrake = false,rmbrake = false;                                  // left and right brakes - non zero values enable brake
int lmcur,rmcur;                                       // left and right motor current

int lmcurmax = 8000;                                   // Max current that can be pulled from the batteries before we stop

unsigned long lastoverload = 0;                            // Time we last overloaded
int overloadtime = 100;

volatile int  lmenc = 0,rmenc = 0;                                       // left and right encoder values

/**
 * Sets up the Arduino ready for use
 */
void setup() {
//      TCCR2B = TCCR2B & B11111000 | B00000110; pwmfreq=6;    // set timer 2 divisor to  256 for PWM frequency of    122.070312500 Hz

  Serial.begin(115200);         // start serial for output

  // Configure motor
  motorsSetup();

  // Configure motor encoders
  encodersSetup();
  
  // initialize i2c
  I2CSetup();
  
  // Start the NeoPixel
  rearLightSetup();
}

/**
 * main loop 
 */
void loop() {
  // Read in the current amps
  lmcur=(analogRead(lmcurpin)-511)*48.83;
  rmcur=(analogRead(rmcurpin)-511)*48.83;  
  
  // Check if we've gone over the limit
  if(lmcur >= lmcurmax || rmcur >= lmcurmax) {
    // Mark the fact that we have overloaded and trigger
    // an update of the Motors, this will cause them to stop
    lastoverload = millis();
    Motors(0, 0);    
  }
  
  // Check if there are any pendign i2c commands to process
  I2C_CheckCommands();
    
  // Update any auto drive
  performAutoDrive();
}



