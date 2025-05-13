// Rover GPS
#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

SoftwareSerial gpsSerial(3, 4);
Adafruit_GPS GPS(&gpsSerial);

float dlat = 0.0;
float dlon = 0.0;

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

  // Leer corrección desde puerto serial
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    if (data.startsWith("DLAT:")) {
      int comma = data.indexOf(',');
      dlat = data.substring(5, comma).toFloat();
      dlon = data.substring(comma + 6).toFloat();
    }
  }

  if (GPS.fix) {
    float corrected_lat = GPS.latitudeDegrees + dlat;
    float corrected_lon = GPS.longitudeDegrees + dlon;

    Serial.print("Corrected Lat: "); Serial.println(corrected_lat, 6);
    Serial.print("Corrected Lon: "); Serial.println(corrected_lon, 6);
    Serial.println("---");

    delay(1000);
  }
}
