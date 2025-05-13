// Base GPS (Arduino)
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

SoftwareSerial gpsSerial(8, 7); // RX, TX
Adafruit_GPS GPS(&gpsSerial);

float lat_base_real = 40.712776; // Coordenada conocida de la base (por ejemplo)
float lon_base_real = -74.005974;

void setup() {
  Serial.begin(115200);
  gpsSerial.begin(9600);
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
}

void loop() {
  GPS.read();
  if (GPS.newNMEAreceived()) {
    if (!GPS.parse(GPS.lastNMEA())) return;
  }

  if (GPS.fix) {
    float dlat = lat_base_real - GPS.latitudeDegrees;
    float dlon = lon_base_real - GPS.longitudeDegrees;

    // Muestra y/o envía al rover
    Serial.print("DLAT:"); Serial.print(dlat, 6);
    Serial.print(",DLON:"); Serial.println(dlon, 6);

    delay(1000); // 1Hz
  }
}
