
#define NO_PORTB_PINCHANGES // to indicate that port b will not be used for pin change interrupts
#define NO_PORTC_PINCHANGES // to indicate that port c will not be used for pin change interrupts


#include <PinChangeInt.h>

void encodersSetup() {
    // Configure motor encoders
  pinMode(lmencpin, INPUT)  ;
  digitalWrite(lmencpin, HIGH);
  PCintPort::attachInterrupt(lmencpin, &leftEncoder, RISING);
  pinMode(rmencpin, INPUT)  ;
  digitalWrite(rmencpin, HIGH);
  PCintPort::attachInterrupt(rmencpin, &rightEncoder, RISING);

}

void leftEncoder() {
  lmenc++;
}

void rightEncoder() {
  rmenc++;
}
