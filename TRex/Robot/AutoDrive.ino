// Code for controlling the robot
int targetDistance = 0;
int distanceTravelled = 0;
boolean autoDriveActive = false;

int oldlmEnc = 0, oldrmEnc = 0;
int kp =5;
unsigned long autoDriveLastChecked = 0;

/**
 * Stops any current auto drive configuration
 */
void stopAutoDrive() {
  autoDriveActive = false;
}

/**
 * Tell the robot to drive forwards a set distance.
 *
 * @param distance - Distance to drive in millimeters
 */
void driveForwards(int distance) {
  int left, right;
  
  Serial.print("Auto drive, distance is ");
  Serial.println(distance);
  
  // Call 'stop' to make sure we are stationary and to reset the encoders
  MotorsStop();
  
  // Configure the target distance and reset
  // the current count
  targetDistance = distance;
  distanceTravelled = 0;
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;
  
  // Start driving
  left = -60;
  right = -60;
  autoDriveActive = true;
  autoDriveLastChecked = millis();
  lmbrake=false;
  rmbrake=false;
  Motors(left, right);
}

/**
 * Tells the robot to rotate the specified number of degrees
 */
void driveRotate(int degreesToTurn) {
  // The number of encoder tickes per degree
  float countsPerDegree = 0.9;
  int left, right;
  
  // Call 'stop' to make sure we are stationary and to reset the encoders
  MotorsStop();

  if(degreesToTurn < 0) {
    left = 60;
    right = -60;
  }
  else {
    left = -60;
    right = 60;
  }
  
  targetDistance = int(abs(countsPerDegree) * degreesToTurn);
  distanceTravelled = 0;
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;
  autoDriveActive = true;
  autoDriveLastChecked = millis();
  lmbrake=false;
  rmbrake=false;
  
  Motors(left, right);    
}

/**
 * Called on each loop to check the status of any in progress
 * auto drive.
 */
void performAutoDrive() {
  // Anything to do?
  if(false == autoDriveActive) {
    return;
  }
  
  // Have we reached (or passed) our destination
  if(targetDistance <= distanceTravelled) {
    Serial.print("Auto drive complete> lmenc:");
    Serial.print(lmenc);
    Serial.print(" rmenc:");
    Serial.println(rmenc);
    
    // We've reach out destination
    MotorsStop();
  }
  // Do we need to check the motors for drift?  
  // We don't want to be constantly checking and correcting
  else if((millis() - autoDriveLastChecked) >= 100) {
    int error = (lmenc - rmenc) / kp;
    autoDriveLastChecked = millis();
    
    // Adjust the right motor speed to keep up with the
    // left motor
    rmspeed += error;
    
    Serial.print("Adjusting for drift ");
    Serial.print((lmenc - rmenc));
    Serial.print(" : ");
    Serial.println(error);
    distanceTravelled += lmenc;
    lmenc = rmenc = 0;
    
  }
  
  // Have we moved?  
  if(oldlmEnc == lmenc && oldrmEnc == rmenc) {
    // We've not moved... so increase power
/*    lmspeed += 1;
    rmspeed += 1;
    lmspeed = min(lmspeed, 255);
    rmspeed = min(rmspeed, 255);
    
    Motors();*/
  }
  else if((targetDistance - distanceTravelled) <= 250) {
    // We are getting closer, so slow down
//    lmspeed = -50;
//    rmspeed = -50;

    
//    Motors();    
  }
    
  // Cache the current encoders  
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;  
}


int autoDriveI2CForwards(byte *i2cArgs, uint8_t *pi2cResponse) {
  int distance;
  
  // Read in the distance
  distance = i2cArgs[0]*256+i2cArgs[1];
  
  // And lets start driving
  driveForwards(distance);

  return 0;
}


int autoDriveI2CRotate(byte *i2cArgs, uint8_t *pi2cResponse) {
  int rotate;
  
  // Read in the distance
  rotate = i2cArgs[0]*256+i2cArgs[1];
  
  // And lets start driving
  driveRotate(rotate);

  return 0;
}



