#include <Adafruit_GPS.h>
#include <SoftwareSerial.h>

// Connect the GPS Power pin to 5V
// Connect the GPS Ground pin to ground
// Connect the GPS TX (transmit) pin to Digital 8
// Connect the GPS RX (receive) pin to Digital 7

// you can change the pin numbers to match your wiring:
SoftwareSerial mySerial(8, 7);
Adafruit_GPS GPS(&mySerial);

// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO  false

void setup()
{
  Serial.begin(115200);
  delay(2000);

  GPS.begin(9600);

  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);

  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  
  GPS.sendCommand(PGCMD_ANTENNA);

  delay(1000);
  Serial.println("lat,lon");
  // Ask for firmware version
  mySerial.println(PMTK_Q_RELEASE);
}

uint32_t timer = millis();
void loop()                     // run over and over again
{
  char c = GPS.read();
  if ((c) && (GPSECHO))
    Serial.write(c);

  if (GPS.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false

    if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
      return;  // we can fail to parse a sentence in which case we should just wait for another
  }

  // approximately every 1 seconds or so, print out the current stats
  if (millis() - timer > 1000) {
    timer = millis(); // reset the timer

    if (GPS.fix) {
      Serial.print(GPS.latitudeDegrees, 6);
      //Serial.print(GPS.lat);
      Serial.print(",");
      Serial.println(GPS.longitudeDegrees, 6);
      //Serial.println(GPS.lon);

      //Serial.print("Speed (knots): "); Serial.println(GPS.speed);
      //Serial.print("Angle: "); Serial.println(GPS.angle);
      //Serial.print("Altitude: "); Serial.println(GPS.altitude);
      //Serial.print("Satellites: "); Serial.println((int)GPS.satellites);
      //Serial.print("Antenna status: "); Serial.println((int)GPS.antenna);
    }
  }
}
