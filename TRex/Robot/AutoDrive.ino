// Code for controlling the robot
int targetDistance = 0;
boolean autoDriveActive = false;

int oldlmEnc = 0, oldrmEnc = 0;

void stopAutoDrive() {
  autoDriveActive = false;
}

void driveForwards(int distance) {
  Serial.print("Auto drive, distance is ");
  Serial.println(distance);
  
  // Call 'stop' to make sure we are stationary and to reset the encoders
  MotorsStop();
  
  targetDistance = distance;
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;
  
  lmspeed = -100;
  rmspeed = -100;
  autoDriveActive = true;
  Motors();
}

void driveRotate(int degreesToTurn) {
  int countsPerDegree = 1;
  
  // Call 'stop' to make sure we are stationary and to reset the encoders
  MotorsStop();

  if(degreesToTurn < 0) {
    lmspeed = 100;
    rmspeed = -100;
  }
  else {
    lmspeed = -100;
    rmspeed = 100;
  }
  
  targetDistance = abs(countsPerDegree * degreesToTurn);
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;
  autoDriveActive = true;
  Motors();    
}


void performAutoDrive() {
  if(false == autoDriveActive) {
    return;
  }
  
  
  if(targetDistance <= lmenc || targetDistance <= rmenc) {
    Serial.print("Auto drive complete> lmenc:");
    Serial.print(lmenc);
    Serial.print(" rmenc:");
    Serial.println(rmenc);
    
    // We've reach out destination
    MotorsStop();
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
  else if((targetDistance - lmenc) <= 250) {
    // We are getting closer, so slow down
//    lmspeed = -50;
//    rmspeed = -50;

    
//    Motors();    
  }
    
  // Cache the current encoders  
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;  
}

