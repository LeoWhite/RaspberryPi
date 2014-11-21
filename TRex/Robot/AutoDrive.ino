// Code for controlling the robot
int targetDistance = 0;
int distanceTravelled = 0;
boolean autoDriveActive = false;

int oldlmEnc = 0, oldrmEnc = 0;
int kp =5;
unsigned long autoDriveLastChecked = 0;

void stopAutoDrive() {
  autoDriveActive = false;
}

void driveForwards(int distance) {
  Serial.print("Auto drive, distance is ");
  Serial.println(distance);
  
  // Call 'stop' to make sure we are stationary and to reset the encoders
  MotorsStop();
  
  targetDistance = distance;
  distanceTravelled = 0;
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;
  
  lmspeed = -150;
  rmspeed = -150;
  autoDriveActive = true;
  autoDriveLastChecked = millis();
  Motors();
}

void driveRotate(int degreesToTurn) {
  float countsPerDegree = 0.9;
  
  // Call 'stop' to make sure we are stationary and to reset the encoders
  MotorsStop();

  if(degreesToTurn < 0) {
    lmspeed = 150;
    rmspeed = -150;
  }
  else {
    lmspeed = -150;
    rmspeed = 150;
  }
  
  targetDistance = int(abs(countsPerDegree) * degreesToTurn);
  oldlmEnc = lmenc;
  oldrmEnc = rmenc;
  autoDriveActive = true;
  Motors();    
}


void performAutoDrive() {
  
  if(false == autoDriveActive) {
    return;
  }
  
  
  if(targetDistance <= distanceTravelled) {
    Serial.print("Auto drive complete> lmenc:");
    Serial.print(lmenc);
    Serial.print(" rmenc:");
    Serial.println(rmenc);
    
    // We've reach out destination
    MotorsStop();
  }
  // Do we need to check the motors for drift?  
  else if((millis() - autoDriveLastChecked) >= 100) {
    int error = (lmenc - rmenc) / kp;
  autoDriveLastChecked = millis();
    
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

