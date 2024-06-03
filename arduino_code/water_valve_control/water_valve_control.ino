// reward duration
float rewardDur = 40;  // ms

// set pin numbers:
//const int audioPin = 5;      // audio monitor pin
const int buttonPin = 7;     // lickport pin
const int valvePin = 9;      // water valve pin
//const int lickEvents = 11;   // lick event pin to turn on when lick is detected
//const int valveEvents = 12;  // valve event pin

// state variables:
//int taskState = 0;        // state of state machine
//int stimState = LOW;      // state of stimulus
//int rewardState = LOW;    // state of reward
//int timeoutState = LOW;   // state of timeout
//int abortState = LOW;     // state of early lick abort
//int winState = LOW;       // state of response window
//int lickState;            // state of lickport
//int lastLickState = LOW;  // state of last lickport sample
int valveState = LOW;     // state of water valve
//int reading = LOW;

// other:
//int lickOn = 0;
//int lickCnt = 0;
//int trialType;
//int trialCnt = 1;
//int cnt = 0;
//char trialStr[6];

// time variables:
// unsigned long t;                     // master time variable in us
// unsigned long lastDebounceTime = 0;  // last debounce time in us
// unsigned long debounceDelay = 1000;  // debounce period in us
// unsigned long lickTime = 0;          // lick timestamp in us
// unsigned long respWinEnd;
// unsigned long rewardEnd;
// unsigned long timeoutEnd;
// float holdTime;
// float respWin;
// float timeoutDur;
// float abortTime;


void setup() {
  pinMode(buttonPin, INPUT);
 // pinMode(audioPin, INPUT);
  pinMode(valvePin, OUTPUT);
 // pinMode(lickEvents, OUTPUT);
 // pinMode(valveEvents, OUTPUT);

  // set states for indicator and valve
  digitalWrite(valvePin, valveState);

  // setup serial port
  //Serial.begin(115200);
  //Serial.read();
  //Serial.println("connected");

  // // retrieve parameters from matlab
  // int done = 0;
  // float val[3];
  // while (!done) {
  //   while (Serial.available() > 0) {
  //     val[cnt] = Serial.parseFloat();
  //     cnt++;
  //     if (cnt > 2) {
  //       done = 1;
  //       holdTime = val[0];
  //       rewardDur = val[1];
  //       debounceDelay = val[2];

  //       Serial.print("HOLDTIME ");
  //       Serial.println(val[0]);
  //       Serial.print("REWTIME ");
  //       Serial.println(val[1]);
  //       Serial.print("DEBOUNCE ");
  //       Serial.println(val[2]);

  //       break;
  //     }
  //   }
  // }





  // clear out the serial
  //Serial.read();
}


void loop() {
 // checkLick();


  if (digitalRead(buttonPin) == HIGH ) {
    // give reward
    //t = micros();
    digitalWrite(valvePin, HIGH);
    delay(rewardDur);
    digitalWrite(valvePin, LOW);
   // t = micros();
   // Serial.print(trialStr);
   // Serial.print(t);
    //Serial.println(" REWARDON");
  }

}





// void checkLick() {
//   // read the state of the switch into a local variable:
//   reading = digitalRead(buttonPin);

//   // check to see if you just pressed the button
//   // (i.e. the input went from LOW to HIGH),  and you've waited
//   // long enough since the last press to ignore any noise:

//   // If the switch changed, due to noise or pressing:
//   if (reading != lastLickState) {
//     // reset the debouncing timer
//     lastDebounceTime = micros();
//   }

//   if ((micros() - lastDebounceTime) > debounceDelay) {
//     // whatever the reading is at, it's been there for longer
//     // than the debounce delay, so take it as the actual current state:

//     // if the button state has changed:
//     if (reading != lickState) {
//       lickState = reading;
//       digitalWrite(lickEvents, lickState);

//       // get timestamp for lick start
//       if (lickState == HIGH) {
//         lickTime = lastDebounceTime;
//         sprintf(trialStr, "%04d ", trialCnt);
//         Serial.print(trialStr);
//         Serial.print(lickTime);
//         Serial.println(" LICK");
//       }
//     }
//   }

//   // save the reading.  Next time through the loop,
//   // it'll be the lastLickState:
//   lastLickState = reading;
// }
