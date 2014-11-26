int volts;                                             // battery voltage*10 (accurate to 1 decimal place)
int xaxis,yaxis,zaxis;                                 // X, Y, Z accelerometer readings
int deltx,delty,deltz;                                 // X, Y, Z impact readings 

/**
 * Returns the current state of the system.
 *
 * @param i2cArgs - Arguments passed via i2c
 * @param pi2cResponse - Filled in with the status
 *
 * @returns the number of response arguments
 */
int getStatus(byte *i2cArgs, uint8_t *pi2cResponse) {
  int i2cResponseLen = 0;
  
  volts=analogRead(voltspin)*10/3.357; 

  // read accelerometer - note analog read takes 260uS for each axis
  xaxis=analogRead(axisxpin);                                 
  yaxis=analogRead(axisypin);
  zaxis=analogRead(axiszpin);
  
  pi2cResponse[i2cResponseLen++] = 0x00;    
    
  pi2cResponse[i2cResponseLen++] = highByte(volts);                   // battery voltage      high byte
  pi2cResponse[i2cResponseLen++] = lowByte(volts);                   // battery voltage      low  byte
  pi2cResponse[i2cResponseLen++] = highByte(lmcur);                   // left  motor current  high byte
  pi2cResponse[i2cResponseLen++] = lowByte(lmcur);                   // left  motor current  low  byte
  
  pi2cResponse[i2cResponseLen++] = highByte(lmenc);                   // left  motor encoder  high byte 
  pi2cResponse[i2cResponseLen++] = lowByte(lmenc);                   // left  motor encoder  low  byte 

  pi2cResponse[i2cResponseLen++]=highByte(rmcur);                   // right motor current  high byte
  pi2cResponse[i2cResponseLen++]= lowByte(rmcur);                   // right motor current  low  byte
  
  pi2cResponse[i2cResponseLen++]=highByte(rmenc);                  // right motor encoder  high byte 
  pi2cResponse[i2cResponseLen++]= lowByte(rmenc);                  // right motor encoder  low  byte 
  
  pi2cResponse[i2cResponseLen++]=highByte(xaxis);                  // accelerometer X-axis high byte
  pi2cResponse[i2cResponseLen++]= lowByte(xaxis);                  // accelerometer X-axis low  byte
  
  pi2cResponse[i2cResponseLen++]=highByte(yaxis);                  // accelerometer Y-axis high byte
  pi2cResponse[i2cResponseLen++]= lowByte(yaxis);                  // accelerometer Y-axis low  byte
  
  pi2cResponse[i2cResponseLen++]=highByte(zaxis);                  // accelerometer Z-axis high byte
  pi2cResponse[i2cResponseLen++]= lowByte(zaxis);                  // accelerometer Z-axis low  byte
  
  pi2cResponse[i2cResponseLen++]=highByte(deltx);                  // X-axis impact data   high byte
  pi2cResponse[i2cResponseLen++]= lowByte(deltx);                  // X-axis impact data   low  byte
  
  pi2cResponse[i2cResponseLen++]=highByte(delty);                  // Y-axis impact data   high byte
  pi2cResponse[i2cResponseLen++]= lowByte(delty);                  // Y-axis impact data   low  byte
  
  pi2cResponse[i2cResponseLen++]=highByte(deltz);                  // Z-axis impact data   high byte
  pi2cResponse[i2cResponseLen++]= lowByte(deltz);                  // Z-axis impact data   low  byte

  return i2cResponseLen;
}

