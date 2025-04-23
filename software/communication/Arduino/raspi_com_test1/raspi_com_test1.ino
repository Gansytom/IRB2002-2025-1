void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println("Hello from Arduino!");
  delay(1000);
}
// run in terminal: sudo chmod a+rw /dev/ttyACM0
