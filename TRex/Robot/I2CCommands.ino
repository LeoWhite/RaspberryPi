#include <Wire.h>

// >> put this into a header file you include at the beginning for better clarity
enum { 
  I2C_CMD_GET_STATE = 0xF,
  I2C_CMD_SET_STATE = 0x10,
  I2C_CMD_STOP = 0x11,
  I2C_CMD_SET_MOTORS = 0x12,
  I2C_CMD_AUTODRIVE_FORWARDS = 0x13,
  I2C_CMD_AUTODRIVE_ROTATE = 0x14
  
};

enum { 
  I2C_MSG_ARGS_MAX = 32,
  I2C_RESP_LEN_MAX = 32
};

extern const byte supportedI2Ccmd[] = { 
  I2C_CMD_GET_STATE,
  I2C_CMD_SET_STATE,
  I2C_CMD_STOP,
  I2C_CMD_SET_MOTORS,
  I2C_CMD_AUTODRIVE_FORWARDS,
  I2C_CMD_AUTODRIVE_ROTATE
  
};

#define SLAVE_ADDRESS 0x07

int argsCnt = 0;                        // how many arguments were passed with given command
int requestedCmd = 0;                   // which command was requested (if any)

byte i2cArgs[I2C_MSG_ARGS_MAX];         // array to store args received from master
int i2cArgsLen = 0;                     // how many args passed by master to given command

uint8_t i2cResponse[I2C_RESP_LEN_MAX];  // array to store response
int i2cResponseLen = 0;                 // response length

int xaxis,yaxis,zaxis;                                 // X, Y, Z accelerometer readings
int deltx,delty,deltz;                                 // X, Y, Z impact readings 
int volts;                                             // battery voltage*10 (accurate to 1 decimal place)

void I2CSetup() {
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);  
}


void I2C_CheckCommands() {
  if(requestedCmd == I2C_CMD_GET_STATE){
    volts=analogRead(voltspin)*10/3.357; 
//    lmcur=(analogRead(lmcurpin)-511)*48.83;
//    rmcur=(analogRead(rmcurpin)-511)*48.83;  
    xaxis=analogRead(axisxpin);                                 // read accelerometer - note analog read takes 260uS for each axis
    yaxis=analogRead(axisypin);
    zaxis=analogRead(axiszpin);
  

    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = 0x0f;    
    i2cResponse[i2cResponseLen++] = 0x00;    
    
  i2cResponse[i2cResponseLen++] = highByte(volts);                   // battery voltage      high byte
  i2cResponse[i2cResponseLen++] = lowByte(volts);                   // battery voltage      low  byte
  i2cResponse[i2cResponseLen++] = highByte(lmcur);                   // left  motor current  high byte
  i2cResponse[i2cResponseLen++] = lowByte(lmcur);                   // left  motor current  low  byte
  
  i2cResponse[i2cResponseLen++] = highByte(lmenc);                   // left  motor encoder  high byte 
  i2cResponse[i2cResponseLen++] = lowByte(lmenc);                   // left  motor encoder  low  byte 

  i2cResponse[i2cResponseLen++]=highByte(rmcur);                   // right motor current  high byte
  i2cResponse[i2cResponseLen++]= lowByte(rmcur);                   // right motor current  low  byte
  
  i2cResponse[i2cResponseLen++]=highByte(rmenc);                  // right motor encoder  high byte 
  i2cResponse[i2cResponseLen++]= lowByte(rmenc);                  // right motor encoder  low  byte 
  
  i2cResponse[i2cResponseLen++]=highByte(xaxis);                  // accelerometer X-axis high byte
  i2cResponse[i2cResponseLen++]= lowByte(xaxis);                  // accelerometer X-axis low  byte
  
  i2cResponse[i2cResponseLen++]=highByte(yaxis);                  // accelerometer Y-axis high byte
  i2cResponse[i2cResponseLen++]= lowByte(yaxis);                  // accelerometer Y-axis low  byte
  
  i2cResponse[i2cResponseLen++]=highByte(zaxis);                  // accelerometer Z-axis high byte
  i2cResponse[i2cResponseLen++]= lowByte(zaxis);                  // accelerometer Z-axis low  byte
  
  i2cResponse[i2cResponseLen++]=highByte(deltx);                  // X-axis impact data   high byte
  i2cResponse[i2cResponseLen++]= lowByte(deltx);                  // X-axis impact data   low  byte
  
  i2cResponse[i2cResponseLen++]=highByte(delty);                  // Y-axis impact data   high byte
  i2cResponse[i2cResponseLen++]= lowByte(delty);                  // Y-axis impact data   low  byte
  
  i2cResponse[i2cResponseLen++]=highByte(deltz);                  // Z-axis impact data   high byte
  i2cResponse[i2cResponseLen++]= lowByte(deltz);                  // Z-axis impact data   low  byte
  requestedCmd = 0;

  }
  else if(requestedCmd == I2C_CMD_STOP){    
    // Send back the command to confirm we recieved it
    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = requestedCmd;    

    MotorsStop();
    
    requestedCmd = 0;
  
  }
  else if(requestedCmd == I2C_CMD_SET_MOTORS && 4 == argsCnt){    
    int i;
    boolean gotLeft = false, gotRight = false;

    
    // Send back the command to confirm we recieved it
    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = requestedCmd;    

    i=i2cArgs[0]*256+i2cArgs[1];                                               // read integer from I²C buffer
    if(i>-256 && i<256)
    {
      lmspeed=i;                                                                 // read new speed for   left  motor
      lmbrake=false;
      gotLeft = true;
    }

    i=i2cArgs[2]*256+i2cArgs[3];                                               // read integer from I²C buffer
    if(i>-256 && i<256)
    {
      rmspeed=i;                                                                 // read new speed for   left  motor
      rmbrake=false;
      gotRight = true;
    }

    if(gotLeft && gotRight) {      
      // The use is now in control, so disable auto drive
      stopAutoDrive();
      
      Motors();
    }
    
    requestedCmd = 0;
  
  }
  else if(requestedCmd == I2C_CMD_AUTODRIVE_FORWARDS && 2 == argsCnt) {
    int distance;
    
    // Send back the command to confirm we recieved it
    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = requestedCmd;    
    
    // Read in the distance
    distance = i2cArgs[0]*256+i2cArgs[1];
    
    // And lets start driving
    driveForwards(distance);

    requestedCmd = 0;    
  }
  else if(requestedCmd == I2C_CMD_AUTODRIVE_ROTATE && 2 == argsCnt) {
    int rotate;
    
    // Send back the command to confirm we recieved it
    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = requestedCmd;    
    
    // Read in the distance
    rotate = i2cArgs[0]*256+i2cArgs[1];
    
    // And lets start driving
    driveRotate(rotate);

    requestedCmd = 0;    
  }  
  else if (requestedCmd != 0){
    // log the requested function is unsupported (e.g. by writing to serial port or soft serial

    requestedCmd = 0;   // set requestd cmd to 0 disabling processing in next loop
  }  
}


// callback for received data
void receiveData(int howMany){
  int cmdRcvd = -1;
  int argIndex = -1; 
  int availableBytes = 0;
  argsCnt = 0;

  if(requestedCmd) {
    Serial.println("Command lost!");
  }

  if (howMany) {
    cmdRcvd = Wire.read();                 // receive first byte - command assumed
    howMany--; // Skip the 'command' byte
    while(howMany--){               // receive rest of tramsmission from master assuming arguments to the command
      if (argIndex < I2C_MSG_ARGS_MAX){
        argIndex++;
        i2cArgs[argIndex] = Wire.read();
      }
      else{
        ; // implement logging error: "too many arguments"
      }
      argsCnt = argIndex+1;  
    }
  }
  else{
    // implement logging error: "empty request"
    return;
  }
  
  // validating command is supported by slave
  int fcnt = -1;
  for (int i = 0; i < sizeof(supportedI2Ccmd); i++) {
    if (supportedI2Ccmd[i] == cmdRcvd) {
      fcnt = i;
    }
  }

  if (fcnt<0){
    // implement logging error: "command not supported"
    Serial.println("not supported");
    return;
  }
  
  // Calculate the checksum
  uint8_t CS = (argsCnt - 1) + 1;
  
  // Starts with the length, followed by the command, followed by all bits of the message
  // excluding the checksum
  CS^=cmdRcvd;
  for (int i = 0; i<(argsCnt - 1); i++){
    CS^=i2cArgs[i];
  } 
  
  // Does it match?
  if(CS != i2cArgs[argsCnt - 1]) {    
    // Perform a stop
    Serial.print("invalid checksum:");
    Serial.println(CS);
    MotorsStop();
    
    return;
  }
  
  // We don't include the checksum in the message
  argsCnt--;
  
  requestedCmd = cmdRcvd;
  // now main loop code should pick up a command to execute and prepare required response when master waits before requesting response
}
// callback for sending data
void sendData(){  
  // Generate the checksum
  // IMPROVE: calculate when generating the message
  uint8_t CS = i2cResponseLen;
  for (int i = 0; i<i2cResponseLen; i++){
    CS^=i2cResponse[i];
  } 

  i2cResponse[i2cResponseLen++] = CS;  
  Wire.write(i2cResponse, i2cResponseLen);
  i2cResponseLen = 0;
}

