


void motorsSetup() {
  pinMode(lmpwmpin,OUTPUT);                            // configure left  motor PWM       pin for output
  pinMode(lmdirpin,OUTPUT);                            // configure left  motor direction pin for output
  pinMode(lmbrkpin,OUTPUT);                            // configure left  motor brake     pin for output
  
  pinMode(rmpwmpin,OUTPUT);                            // configure right motor PWM       pin for output
  pinMode(rmdirpin,OUTPUT);                            // configure right motor direction pin for output
  pinMode(rmbrkpin,OUTPUT);                            // configure right motor brake     pin for output
  
}



void Motors()
{ 
  static boolean oldlmbrake = true, oldrmbrake = true;

  // Are we in an 'overload' state?
  if((millis() - lastoverload) < overloadtime)
  {
    // Set speed to zero and brakes to on
    lmspeed = 0;
    lmbrake=true;
    rmspeed = 0;
    rmbrake=true;
  }
  
  if(oldlmbrake != lmbrake) {
    digitalWrite(lmbrkpin,lmbrake);                     // if left brake>0 then engage electronic braking for left motor
    oldlmbrake = lmbrake;
  }
  digitalWrite(lmdirpin,lmspeed>0);                     // if left speed>0 then left motor direction is forward else reverse
  analogWrite (lmpwmpin,abs(lmspeed/2));                  // set left PWM to absolute value of left speed - if brake is engaged then PWM controls braking
  if(lmbrake>0 && lmspeed==0) lmenc=0;                  // if left brake is enabled and left speed=0 then reset left encoder counter
  
  if(oldrmbrake != rmbrake) {
    digitalWrite(rmbrkpin,rmbrake);                     // if right brake>0 then engage electronic braking for right motor#
  }
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


