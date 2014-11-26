

/**
 * Configures the Arduino's pins that will be used to control the motors
 */
void motorsSetup() {
  // Setup the left motor
  pinMode(lmpwmpin,OUTPUT);
  pinMode(lmdirpin,OUTPUT);
  pinMode(lmbrkpin,OUTPUT);
  
  // Setup the right motor
  pinMode(rmpwmpin,OUTPUT);
  pinMode(rmdirpin,OUTPUT);
  pinMode(rmbrkpin,OUTPUT);
}

/** 
 * Updates the motors based on the current settings
 */
void Motors()
{ 
  // Are we in an 'overload' state?
  if((millis() - lastoverload) < overloadtime)
  {
    // Set speed to zero and brakes to on
    lmspeed = 0;
    lmbrake=true;
    rmspeed = 0;
    rmbrake=true;
  }
  
  digitalWrite(lmbrkpin,lmbrake);                     // if left brake>0 then engage electronic braking for left motor
  digitalWrite(lmdirpin,lmspeed>0);                     // if left speed>0 then left motor direction is forward else reverse
  analogWrite (lmpwmpin,abs(lmspeed/2));                  // set left PWM to absolute value of left speed - if brake is engaged then PWM controls braking
  if(lmbrake>0 && lmspeed==0) lmenc=0;                  // if left brake is enabled and left speed=0 then reset left encoder counter
  
  digitalWrite(rmbrkpin,rmbrake);                     // if right brake>0 then engage electronic braking for right motor#
  digitalWrite(rmdirpin,rmspeed>0);                     // if right speed>0 then right motor direction is forward else reverse
  analogWrite (rmpwmpin,abs(rmspeed/2));                  // set right PWM to absolute value of right speed - if brake is engaged then PWM controls braking
  if(rmbrake>0 && rmspeed==0) rmenc=0;                  // if right brake is enabled and right speed=0 then reset right encoder counter
  
  
  // Update the LEDS
  rearLightUpdate();
  
  Serial.print("Motors :");
  Serial.print(lmspeed);
  Serial.print(":");
  Serial.println(rmspeed);
}

/**
 * Stops the motors and enables the brakes
 */
void MotorsStop() {
  // Set speed to zero and brakes to on
  lmspeed = 0;
  lmbrake=true;
  rmspeed = 0;
  rmbrake=true;
  
  // Stopping the motors also cancels auto drive
  stopAutoDrive();
  Motors();
}

/**
 * Process the i2c stop command
 */
int motorsI2CStop(byte *i2cArgs, uint8_t *pi2cResponse) {
  // No arguments to process, so just stop the motors
  MotorsStop();
  
  return 0;
}

/**
 * Process the i2c set motors command
 *
 * Takes in the two integers that contain the power levels
 * of the left and right motors
 */
int motorsI2CSet(byte *i2cArgs, uint8_t *pi2cResponse) {
  int i;
  boolean gotLeft = false, gotRight = false;
  int i2cResponseLen = 0;

  // read integer from I²C buffer
  i=i2cArgs[0]*256+i2cArgs[1];                                               
  if(i>-256 && i<256)
  {
    lmspeed=i;                                                                 
    lmbrake=false;
    gotLeft = true;
  }

  // read integer from I²C buffer
  i=i2cArgs[2]*256+i2cArgs[3];
  if(i>-256 && i<256)
  {
    rmspeed=i;
    rmbrake=false;
    gotRight = true;
  }

  if(gotLeft && gotRight) {      
    // The user is now in control, so disable auto drive
    stopAutoDrive();
    
    Motors();
  }
    
  return i2cResponseLen;
}
