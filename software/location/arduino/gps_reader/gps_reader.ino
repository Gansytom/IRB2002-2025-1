#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

SoftwareSerial gpsSerial(8, 7);  // RX, TX
Adafruit_GPS GPS(&gpsSerial);
#define GPSECHO  false

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600);
  GPS.begin(9600);

  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); // 1 Hz

  delay(1000);
  Serial.println("lat,lon");
}

void loop() {
  GPS.read();
  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA())) return;
  }

  if (GPS.fix) {
    Serial.print(GPS.latitudeDegrees, 6);
    Serial.print(",");
    Serial.println(GPS.longitudeDegrees, 6);
  }

  delay(1000);  // 1 lectura por segundo
}
