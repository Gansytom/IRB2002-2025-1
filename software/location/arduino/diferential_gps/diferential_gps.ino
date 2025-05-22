#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

// Connect the GPS Power pin to 5V
// Connect the GPS Ground pin to ground
// Connect the GPS TX (transmit) pin to Digital 8 for GPS1
// Connect the GPS RX (receive) pin to Digital 7 for GPS1
// Connect the GPS TX (transmit) pin to Digital 6 for GPS2
// Connect the GPS RX (receive) pin to Digital 5 for GPS2

// you can change the pin numbers to match your wiring:
SoftwareSerial GPS1Serial(8, 7);
Adafruit_GPS GPS1(&GPS1Serial);

SoftwareSerial GPS2Serial(6, 5);
Adafruit_GPS GPS2(&GPS2Serial);

// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO  true

void setup()
{
  Serial.begin(115200);
  delay(2000);

  GPS1.begin(9600);
  GPS2.begin(4800);

  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS1.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS2.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  GPS1.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  GPS2.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);

  // Set the update rate
  GPS1.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  GPS2.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  
  GPS1.sendCommand(PGCMD_ANTENNA);
  GPS2.sendCommand(PGCMD_ANTENNA);

  delay(1000);
  Serial.println("lat,lon");
  // Ask for firmware version
  GPS1Serial.println(PMTK_Q_RELEASE);
  GPS2Serial.println(PMTK_Q_RELEASE);
}

uint32_t timer = millis();
void loop()                     // run over and over again
{
  char c1 = GPS1.read();
  if ((c1) && (GPSECHO))
    Serial.write(c1);

  char c2 = GPS2.read();
  if ((c2) && (GPSECHO))
    Serial.write(c2);

  if (GPS1.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false

    if (!GPS1.parse(GPS1.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
      return;  // we can fail to parse a sentence in which case we should just wait for another
  }

  if (GPS2.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false

    if (!GPS2.parse(GPS2.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
      return;  // we can fail to parse a sentence in which case we should just wait for another
  }

  // approximately every 1 seconds or so, print out the current stats
  if (millis() - timer > 1000) {
    timer = millis(); // reset the timer

    if (GPS1.fix) {
      Serial.print("GPS1->");
      Serial.print(GPS1.latitudeDegrees, 6);
      Serial.print(",");
      Serial.println(GPS1.longitudeDegrees, 6);
    }

    if (GPS2.fix) {
      Serial.print("GPS2->");
      Serial.print(GPS2.latitudeDegrees, 6);
      Serial.print(",");
      Serial.println(GPS2.longitudeDegrees, 6);
    }
  }
}
