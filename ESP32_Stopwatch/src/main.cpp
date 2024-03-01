#include <Arduino.h>
#include <EasyButton.h>
#include <RemoteStopwatch.h>
#include <LocalStopwatch.h>
#include <StopwatchInterface.h>

#define DEBOUNCE_MS 50
#define ENABLE_PULLUP true
#define ACTIVE_LOW false
#define LONG_PRESS_MS 2000
#define STOP_BUTTON_LONG_PRESS_MS 700
#define DISPLAY_UPDATE_INTERVAL 100 

EasyButton startButton(25, DEBOUNCE_MS, ENABLE_PULLUP, ACTIVE_LOW);
EasyButton stopButton(26, DEBOUNCE_MS, ENABLE_PULLUP, ACTIVE_LOW);
EasyButton lapButton(27, DEBOUNCE_MS, ENABLE_PULLUP, ACTIVE_LOW);
EasyButton resetButton(12, DEBOUNCE_MS, ENABLE_PULLUP, ACTIVE_LOW);
EasyButton buzzerButton(14, DEBOUNCE_MS, ENABLE_PULLUP, ACTIVE_LOW); //here the buzzer should be connected. Also 2 or more can be connected in parallel from GND to this input pin
bool buzzerButtonIsPressed_flag = false; //this is needed to save if the buzzer is currently pressed
bool stopButtonIsPressed_flag = false; //this is needed to save if the stop button is currently pressed
bool isConnectedToPC = false;

StopwatchInterface * stopwatch;

void setup() {
  stopButton.begin();
  startButton.begin();
  lapButton.begin();
  resetButton.begin();
  buzzerButton.begin();

  //if the start button is pressed during boot, the esp32 will connect to the pc
  if (!startButton.isPressed()){ //the isPressed returns the opposite of the expected value!
    isConnectedToPC = true;
  }

  if (isConnectedToPC){
    stopwatch = new RemoteStopwatch(); //use the stopwatch that is running on the pc written in python. The RemoteStopwatch is just an interface that sends commands via Serial to the Stopwatch
  }
  else{
    stopwatch = new LocalStopwatch(); //use the stopwatch that is running on the esp32. The results are shown on an lcd display
  }

  //button callbacks
    stopButton.onPressed([]() { stopwatch->stop(); });
    startButton.onPressed([]() { stopwatch->start(); });
    lapButton.onPressed([]() { stopwatch->lap(); });
    resetButton.onPressed([]() { stopwatch->reset(); });
    buzzerButton.onPressed([]() { stopwatch->buzzer(); });
}

void loop() {
  stopButton.read();
  startButton.read();
  lapButton.read();
  resetButton.read();
  buzzerButton.read();

  //This checks if the button is long pressed. The function name "".releasedFor" is misleading and does not work as expected
  //Also the method "onPressedFor" does not work as expected. Thats why i made it like this.
  if (buzzerButton.releasedFor(LONG_PRESS_MS) && !buzzerButtonIsPressed_flag) {
    stopwatch->buzzer_longpress();
    buzzerButtonIsPressed_flag = true;
  }

  if (buzzerButton.wasReleased()) {
    buzzerButtonIsPressed_flag = false;
  }

  if (stopButton.releasedFor(STOP_BUTTON_LONG_PRESS_MS) && !stopButtonIsPressed_flag) {
    stopwatch->stop_longpress();
    stopButtonIsPressed_flag = true;
  }

  if (stopButton.wasReleased()) {
    stopButtonIsPressed_flag = false;
  }

  //update the display every 100ms
  int updateDisplayInterval = DISPLAY_UPDATE_INTERVAL;
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate > updateDisplayInterval) {
    lastDisplayUpdate = millis();
    stopwatch->updateDisplay();
  }

}



