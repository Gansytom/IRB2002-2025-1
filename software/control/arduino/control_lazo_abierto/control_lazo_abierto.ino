int LL_PWM = 6;
int LR_PWM = 5;
int RL_PWM = 10;
int RR_PWM = 11;
int RELE = 7;

void setup() {
 pinMode(LL_PWM, OUTPUT);
 pinMode(LR_PWM, OUTPUT);
 pinMode(RL_PWM, OUTPUT);
 pinMode(RR_PWM, OUTPUT);
 pinMode(RELE, OUTPUT);
 Serial.begin(9600);
 digitalWrite(RELE, HIGH);
}

void loop() {
  int velocidad_max = 0; // Valor entre 0 y 254
  
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.print("You sent me: ");
    Serial.println(data);
    data.trim(); // Elimina espacios o saltos de línea adicionales

    // Separar los dos valores de velocidad
    int separator = data.indexOf(';');
    if (separator != -1) {
      String izq_str = data.substring(0, separator);
      String der_str = data.substring(separator + 1);
      
      int vel_izq = izq_str.toInt();
      int vel_der = der_str.toInt();

      Serial.print("Referancia Izquierda: ");
      Serial.println(vel_izq);
      Serial.print(" | Referencia Derecha: ");
      Serial.println(vel_der);

      // Control motor izquierdo
      if (vel_izq >= 0) {
        analogWrite(LL_PWM, vel_izq);
        analogWrite(LR_PWM, 0);
      } else {
        analogWrite(LL_PWM, 0);
        analogWrite(LR_PWM, -vel_izq);
      }

      // Control motor derecho
      if (vel_der >= 0) {
        analogWrite(RL_PWM, vel_der);
        analogWrite(RR_PWM, 0);
      } else {
        analogWrite(RL_PWM, 0);
        analogWrite(RR_PWM, -vel_der);
      }
    } else {
      Serial.println("Formato inválido. Usa: <vel_izq>;<vel_der>");
    }
  }
}
