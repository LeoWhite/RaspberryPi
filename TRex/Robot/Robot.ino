#include <Wire.h>
#include "IOpins.h"

// >> put this into a header file you include at the beginning for better clarity
enum { 
  I2C_CMD_GET_STATE = 0xF,
  I2C_CMD_SET_STATE = 2
};

enum { 
  I2C_MSG_ARGS_MAX = 32,
  I2C_RESP_LEN_MAX = 32
};

extern const byte supportedI2Ccmd[] = { 
  I2C_CMD_GET_STATE,
  2
};

#define SLAVE_ADDRESS 0x07
int number = 0;
int state = 0;

int argsCnt = 0;                        // how many arguments were passed with given command
int requestedCmd = 0;                   // which command was requested (if any)

byte i2cArgs[I2C_MSG_ARGS_MAX];         // array to store args received from master
int i2cArgsLen = 0;                     // how many args passed by master to given command

uint8_t i2cResponse[I2C_RESP_LEN_MAX];  // array to store response
int i2cResponseLen = 0;                 // response length

// define global variables here
byte mode=0;                                           // mode=0: I2C / mode=1: Radio Control / mode=2: Bluetooth / mode=3: Shutdown
int  lowbat=550;                                       // default low battery voltage is 5.5V
byte errorflag;                                        // non zero if bad data packet received
byte pwmfreq;                                          // value from 1-7
byte i2cfreq;                                          // I2C clock frequency can be 100kHz(default) or 400kHz
byte I2Caddress;                                       // I2C slave address
int lmspeed,rmspeed;                                   // left and right motor speeds -255 to +255
byte lmbrake,rmbrake;                                  // left and right brakes - non zero values enable brake
int lmcur,rmcur;                                       // left and right motor current
int lmenc = 0,rmenc = 0;                                       // left and right encoder values
int volts;                                             // battery voltage*10 (accurate to 1 decimal place)
int xaxis,yaxis,zaxis;                                 // X, Y, Z accelerometer readings
int deltx,delty,deltz;                                 // X, Y, Z impact readings 
int magnitude;                                         // impact magnitude
byte devibrate=50;                                     // number of 2mS intervals to wait after an impact has occured before a new impact can be recognized
int sensitivity=50;                                    // minimum magnitude required to register as an impact


void setup() {
    Serial.begin(9600);         // start serial for output
    // initialize i2c as slave
    Wire.begin(SLAVE_ADDRESS);

    // define callbacks for i2c communication
    Wire.onReceive(receiveData);
    Wire.onRequest(sendData);
}

void loop() {
  
  if(requestedCmd == I2C_CMD_GET_STATE){
    volts=analogRead(voltspin)*10/3.357; 
    lmcur=(analogRead(lmcurpin)-511)*48.83;
    rmcur=(analogRead(rmcurpin)-511)*48.83;  
    xaxis=analogRead(axisxpin);                                 // read accelerometer - note analog read takes 260uS for each axis
    yaxis=analogRead(axisxpin);
    zaxis=analogRead(axisxpin);
  

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
  else if (requestedCmd != 0){
    // log the requested function is unsupported (e.g. by writing to serial port or soft serial

    requestedCmd = 0;   // set requestd cmd to 0 disabling processing in next loop
  }
}

// callback for received data
void receiveData(int howMany){
  int cmdRcvd = -1;
  int argIndex = -1; 
  argsCnt = 0;

  if (Wire.available()){
    cmdRcvd = Wire.read();                 // receive first byte - command assumed
    while(Wire.available()){               // receive rest of tramsmission from master assuming arguments to the command
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
    return;
  }
  requestedCmd = cmdRcvd;
  // now main loop code should pick up a command to execute and prepare required response when master waits before requesting response
}
// callback for sending data
void sendData(){
  Wire.write(i2cResponse, i2cResponseLen);
}


