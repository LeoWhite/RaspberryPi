#include <Adafruit_NeoPixel.h>
#include <Wire.h>
#include "IOpins.h"

// >> put this into a header file you include at the beginning for better clarity
enum { 
  I2C_CMD_GET_STATE = 0xF,
  I2C_CMD_SET_STATE = 0x10,
  I2C_CMD_STOP = 0x11,
  I2C_CMD_SET_MOTORS = 0x12,
  
};

enum { 
  I2C_MSG_ARGS_MAX = 32,
  I2C_RESP_LEN_MAX = 32
};

extern const byte supportedI2Ccmd[] = { 
  I2C_CMD_GET_STATE,
  I2C_CMD_SET_STATE,
  I2C_CMD_STOP,
  I2C_CMD_SET_MOTORS
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
boolean lmbrake = false,rmbrake = false;                                  // left and right brakes - non zero values enable brake
int lmcur,rmcur;                                       // left and right motor current
int lmcurmax = 8000;                                   // Max current that can be pulled from the batteries before we stop
unsigned long lastoverload = 0;                            // Time we last overloaded
int overloadtime = 100;

volatile int  lmenc = 0,rmenc = 0;                                       // left and right encoder values
int volts;                                             // battery voltage*10 (accurate to 1 decimal place)
int xaxis,yaxis,zaxis;                                 // X, Y, Z accelerometer readings
int deltx,delty,deltz;                                 // X, Y, Z impact readings 
int magnitude;                                         // impact magnitude
byte devibrate=50;                                     // number of 2mS intervals to wait after an impact has occured before a new impact can be recognized
int sensitivity=50;                                    // minimum magnitude required to register as an impact

void setup() {
//      TCCR2B = TCCR2B & B11111000 | B00000110; pwmfreq=6;    // set timer 2 divisor to  256 for PWM frequency of    122.070312500 Hz

    Serial.begin(115200);         // start serial for output

  // Configure motor pins    
  pinMode(lmpwmpin,OUTPUT);                            // configure left  motor PWM       pin for output
  pinMode(lmdirpin,OUTPUT);                            // configure left  motor direction pin for output
  pinMode(lmbrkpin,OUTPUT);                            // configure left  motor brake     pin for output
  
  pinMode(rmpwmpin,OUTPUT);                            // configure right motor PWM       pin for output
  pinMode(rmdirpin,OUTPUT);                            // configure right motor direction pin for output
  pinMode(rmbrkpin,OUTPUT);                            // configure right motor brake     pin for output
  
  // Configure motor encoders
  encodersSetup();
  
  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  
  // Start the NeoPixel
  rearLightSetup();
}

void loop() {
  // Read in the current amps
  lmcur=(analogRead(lmcurpin)-511)*48.83;
  rmcur=(analogRead(rmcurpin)-511)*48.83;  
  
  // Check if we've gone over the limit
  if(lmcur >= lmcurmax || rmcur >= lmcurmax) {
    // Mark the fact that we have overloaded and trigger
    // an update of the Motors, this will cause them to stop
    lastoverload = millis();
    Motors();    
  }
  
  if(requestedCmd == I2C_CMD_GET_STATE){
    volts=analogRead(voltspin)*10/3.357; 
//    lmcur=(analogRead(lmcurpin)-511)*48.83;
//    rmcur=(analogRead(rmcurpin)-511)*48.83;  
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
  else if(requestedCmd == I2C_CMD_STOP){    
    // Send back the command to confirm we recieved it
    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = I2C_CMD_STOP;    

    // Set speed to zero and brakes to on
    lmspeed = 0;
    lmbrake=true;
    rmspeed = 0;
    rmbrake=true;
    
    Motors();
    
    requestedCmd = 0;
  
  }
  else if(requestedCmd == I2C_CMD_SET_MOTORS && 4 == argsCnt){    
    int i;
    boolean gotLeft = false, gotRight = false;

    
    // Send back the command to confirm we recieved it
    i2cResponseLen = 0;
    i2cResponse[i2cResponseLen++] = I2C_CMD_SET_MOTORS;    

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
      Motors();
    }
    
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
    lmspeed = 0;
    lmbrake=true;
    rmspeed = 0;
    rmbrake=true;
    Motors();    
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
  analogWrite (lmpwmpin,abs(lmspeed));                  // set left PWM to absolute value of left speed - if brake is engaged then PWM controls braking
  if(lmbrake>0 && lmspeed==0) lmenc=0;                  // if left brake is enabled and left speed=0 then reset left encoder counter
  
  if(oldrmbrake != rmbrake) {
    digitalWrite(rmbrkpin,rmbrake);                     // if right brake>0 then engage electronic braking for right motor#
  }
  digitalWrite(rmdirpin,rmspeed>0);                     // if right speed>0 then right motor direction is forward else reverse
  analogWrite (rmpwmpin,abs(rmspeed));                  // set right PWM to absolute value of right speed - if brake is engaged then PWM controls braking
  if(rmbrake>0 && rmspeed==0) rmenc=0;                  // if right brake is enabled and right speed=0 then reset right encoder counter
  
  
  // Update the LEDS
  rearLightUpdate();
  
  Serial.print("Motors :");
  Serial.print(lmspeed);
  Serial.print(":");
  Serial.println(rmspeed);
}





